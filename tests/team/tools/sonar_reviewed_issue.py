"""Replay one independently reviewed issue disposition on the disposable PR scanner."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from time import sleep

import requests


SCOPED_PATHS = ("backend", "frontend", "sonar-project.properties", "requirements-test.txt",
                "tests/team/api/test_auth_transport.py", "tests/team/conftest.py", "tests/team/phase2_support.py")
CI_SONAR = "http://127.0.0.1:9000"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def git_check(*command):
    return subprocess.run(["git", *command], check=False).returncode == 0


def request(client, method, url, **kwargs):
    response = client.request(method, url, timeout=25, allow_redirects=False, **kwargs)
    response.raise_for_status()
    if not 200 <= response.status_code < 300:
        raise RuntimeError(f"Unexpected HTTP {response.status_code} from {url}")
    return response


def approvals_match(client, repo, decision):
    api = f"https://api.github.com/repos/{repo}"
    records = request(client, "GET", f"{api}/pulls/{decision['pull_request']}/reviews",
                      params={"per_page": 100})
    if "next" in records.links:
        return False
    reviews = records.json()
    pinned = {row["id"]: row for row in reviews}
    substantive = {row["user"]["login"]: row for row in reviews
                   if row["state"] in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}}
    for review in decision["reviews"]:
        row = pinned.get(review["approval_id"], {})
        if (row.get("user", {}).get("login"), row.get("state"), row.get("commit_id")) != (
            review["author"], "APPROVED", decision["reviewed_revision"]
        ) or substantive.get(review["author"], {}).get("state") != "APPROVED":
            return False
        comment = request(client, "GET", f"{api}/issues/comments/{review['comment_id']}").json()
        body = comment["body"].replace("\r\n", "\n")
        if (comment["user"]["login"] != review["author"] or
                comment["issue_url"] != f"{api}/issues/{decision['pull_request']}" or
                sha256(body.encode()).hexdigest() != review["body_sha256"]):
            return False
    return True


def eligible_findings(issues, project, fingerprint):
    return [issue for issue in issues if (issue["rule"], issue["component"], issue.get("line"),
                                           issue.get("hash"), issue.get("issueStatus")) == (
        fingerprint["rule"], f"{project}:{fingerprint['file']}", fingerprint["line"], fingerprint["hash"], "OPEN"
    )]


def replay(project, decision, baseline):
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr = os.environ.get("PR_NUMBER", "")
    if (not pr.isdecimal() or
        (os.environ.get("GITHUB_ACTIONS"), os.environ.get("GITHUB_EVENT_NAME"),
         os.environ.get("SONAR_HOST_URL"), repo, os.environ.get("HEAD_REPOSITORY"), project) != (
            "true", "pull_request", CI_SONAR, decision["repository"], decision["repository"], f"medihub-pr-{pr}"
        )
    ):
        return {"result": "skipped", "reason": "Not the authorized disposable PR scanner"}
    source = decision["candidate_revision"]
    if not (git_check("merge-base", "--is-ancestor", source, baseline) and
            git_check("merge-base", "--is-ancestor", baseline, "HEAD") and
            git_check("diff", "--quiet", source, baseline, "--", *SCOPED_PATHS)):
        return {"result": "skipped", "reason": "Base application differs from the originally reviewed source"}
    # Require byte-for-byte equality with the specific Phase 3 application and
    # verify that the only differences from the reviewed base are its UI files.
    presentation = decision["phase3_presentation_revision"]
    if not (git_check("merge-base", "--is-ancestor", presentation, "HEAD") and
            git_check("diff", "--quiet", presentation, "HEAD", "--", *SCOPED_PATHS) and
            git_check("diff", "--quiet", baseline, "HEAD", "--", *SCOPED_PATHS,
                      ":(exclude)frontend/custom.css", ":(exclude)frontend/js/patient.js")):
        return {"result": "skipped", "reason": "Candidate differs from the verified Phase 3 presentation revision"}

    proof = read_json(decision["local_evidence"])
    local = proof["issue"]
    fingerprint = decision["finding"]
    transitioned = any(diff["key"] == "issueStatus" and diff.get("newValue") == "FALSE_POSITIVE"
                       for event in proof["history"] for diff in event["diffs"])
    if (not transitioned or local["issueStatus"] != "FALSE_POSITIVE"
            or (local["key"], local["rule"], local["hash"], local["line"], local["component"]) != (
                decision["local_issue_key"], fingerprint["rule"], fingerprint["hash"], fingerprint["line"],
                f"medihub-phase2-candidate:{fingerprint['file']}")):
        return {"result": "skipped", "reason": "Local disposition evidence did not match"}

    with requests.Session() as github:
        github.headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
        if not approvals_match(github, repo, decision):
            return {"result": "skipped", "reason": "Independent reviews or technical comments changed"}

    with requests.Session() as sonar:
        sonar.trust_env = False
        sonar.headers["Authorization"] = "Bearer " + os.environ["SONAR_TOKEN"]

        def issues(params):
            return request(sonar, "GET", CI_SONAR + "/api/issues/search", params=params).json()["issues"]

        matching = eligible_findings(issues({"componentKeys": project, "rules": fingerprint["rule"]}),
                                    project, fingerprint)
        if len(matching) != 1:
            return {"result": "skipped", "reason": f"Found {len(matching)} exact open matches"}
        finding = matching[0]
        key = finding["key"]
        note = ("Phase 2 reviewed false positive for header-only JWT. All 14 protected write routes rejected "
                "cookie-only authentication. The public auth routes set no authenticated cookie, and five "
                f"CORS preflights granted neither origins nor credentials. Local issue {local['key']}. "
                f"Independent reviewer evidence: https://github.com/{repo}/pull/{decision['pull_request']}.")
        request(sonar, "POST", CI_SONAR + "/api/issues/add_comment", data={"issue": key, "text": note})
        request(sonar, "POST", CI_SONAR + "/api/issues/do_transition",
                data={"issue": key, "transition": "falsepositive"})
        resolved = issues({"issues": key, "additionalFields": "comments"})
        for _ in range(10):
            if len(resolved) == 1 and resolved[0].get("issueStatus") == "FALSE_POSITIVE":
                break
            sleep(1)
            resolved = issues({"issues": key, "additionalFields": "comments"})
        else:
            raise RuntimeError("Sonar did not confirm the reviewed transition")
        history = request(sonar, "GET", CI_SONAR + "/api/issues/changelog", params={"issue": key}).json()
    return {"result": "applied", "reviewed_revision": decision["reviewed_revision"],
            "reviewed_candidate_revision": source, "baseline_revision": baseline,
            "local_issue_key": local["key"], "reviews": decision["reviews"],
            "before": finding, "after": resolved[0], "history": history["changelog"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("decision", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args()
    result = replay(args.project, read_json(args.decision), args.baseline)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Reviewed Sonar disposition:", result["result"], result.get("reason", "confirmed by SonarQube API"))


if __name__ == "__main__":
    main()
