# Booking control-flow graph

`backend/routes/patient.py:212` through line 337. Each explicit return joins one exit. One decision is counted per condition, with an explicit handled-exception edge per handler. Uncaught runtime exceptions and framework decorators are outside the function CFG.

- Concrete graph: E = 89, N = 68, P = 1. M = **23**.
- Short-circuit variant: E = 99, N = 73, P = 1. M = **28**.

```mermaid
flowchart TD
    N1["1. entry"]
    N2["2. exit"]
    N3["3. L337 return jsonify({'success': True, 'message': 'Appointment booked successfully', 'da..."]
    N4["4. L335 db.session.commit()"]
    N5["5. L334 db.session.add(appointment)"]
    N6["6. L325 appointment = Appointment(doctor_id=doctor_id, patient_id=patient.id, appointment_..."]
    N7["7. L322 return (jsonify({'success': False, 'message': 'You already have an appointment at ..."]
    N8["8. L321 patient_conflict"]
    N9["9. L314 patient_conflict = Appointment.query.filter_by(patient_id=patient.id, appointment_..."]
    N10["10. L311 return (jsonify({'success': False, 'message': 'This slot is already booked'}), 400)"]
    N11["11. L310 existing_booking"]
    N12["12. L303 existing_booking = Appointment.query.filter_by(doctor_id=doctor_id, appointment_da..."]
    N13["13. L300 return (jsonify({'success': False, 'message': f'Doctor is not available for {slot_..."]
    N14["14. L299 not availability"]
    N15["15. L292 availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, availabilit..."]
    N16["16. L289 return (jsonify({'success': False, 'message': f'Cannot book this slot for today as..."]
    N17["17. L288 current_hour >= hour"]
    N18["18. L287 apt_date == today"]
    N19["19. L280 slot_type = 'morning'"]
    N20["20. L282 slot_type = 'evening'"]
    N21["21. L284 return (jsonify({'success': False, 'message': 'Invalid time slot. Only Morning (09..."]
    N22["22. L281 15 <= hour < 19"]
    N23["23. L279 9 <= hour < 13"]
    N24["24. L278 hour = apt_time.hour"]
    N25["25. L275 return (jsonify({'success': False, 'message': 'Notes must be text'}), 400)"]
    N26["26. L274 notes is not None and (not isinstance(notes, str))"]
    N27["27. L273 notes = data.get('notes', '')"]
    N28["28. L267 try"]
    N29["29. L269 apt_time = datetime.strptime(start, '%H:%M').time()"]
    N30["30. L268 start = time_str.split('-', 1)[0].strip() if '-' in time_str else time_str"]
    N31["31. L271 return (jsonify({'success': False, 'message': 'Invalid appointment time format'}),..."]
    N32["32. L266 return (jsonify({'success': False, 'message': 'Invalid appointment time format'}),..."]
    N33["33. L265 not isinstance(time_str, str)"]
    N34["34. L264 time_str = data['appointment_time']"]
    N35["35. L261 return (jsonify({'success': False, 'message': 'Cannot book appointments for past d..."]
    N36["36. L260 apt_date < today"]
    N37["37. L258 current_minute = now.minute"]
    N38["38. L257 current_hour = now.hour"]
    N39["39. L256 today = now.date()"]
    N40["40. L255 now = datetime.utcnow() + timedelta(hours=5, minutes=30)"]
    N41["41. L248 try"]
    N42["42. L249 apt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()"]
    N43["43. L251 return (jsonify({'success': False, 'message': 'Invalid date format'}), 400)"]
    N44["44. L246 return (jsonify({'success': False, 'message': 'Doctor not found or inactive'}), 404)"]
    N45["45. L245 doctor is None or not doctor.is_active"]
    N46["46. L244 doctor = Doctor.query.get(doctor_id)"]
    N47["47. L242 return (jsonify({'success': False, 'message': 'Doctor ID must be an integer'}), 400)"]
    N48["48. L241 type(doctor_id) is not int or not -2 ** 63 <= doctor_id < 2 ** 63"]
    N49["49. L237 try"]
    N50["50. L238 doctor_id = int(doctor_id)"]
    N51["51. L240 return (jsonify({'success': False, 'message': 'Doctor ID must be an integer'}), 400)"]
    N52["52. L236 isinstance(doctor_id, str) and doctor_id.isascii() and doctor_id.isdecimal()"]
    N53["53. L235 doctor_id = data['doctor_id']"]
    N54["54. L233 return (jsonify({'success': False, 'message': 'Appointment time is required'}), 400)"]
    N55["55. L232 not data.get('appointment_time')"]
    N56["56. L230 return (jsonify({'success': False, 'message': 'Appointment date is required'}), 400)"]
    N57["57. L229 not data.get('appointment_date')"]
    N58["58. L227 return (jsonify({'success': False, 'message': 'Doctor ID is required'}), 400)"]
    N59["59. L226 not data.get('doctor_id')"]
    N60["60. L224 return (jsonify({'success': False, 'message': 'Booking requires a JSON object'}), ..."]
    N61["61. L223 not isinstance(data, dict)"]
    N62["62. L222 data = request.get_json(silent=True)"]
    N63["63. L220 return (jsonify({'success': False, 'message': 'Your account has been blacklisted. ..."]
    N64["64. L219 patient.is_blacklisted"]
    N65["65. L217 return (jsonify({'success': False, 'message': 'Patient profile not found'}), 404)"]
    N66["66. L216 patient is None"]
    N67["67. L214 patient = Patient.query.filter_by(user_id=user_id).first()"]
    N68["68. L213 user_id = get_current_user_id()"]
    N3 -->|1 | N2
    N4 -->|2 | N3
    N5 -->|3 | N4
    N6 -->|4 | N5
    N7 -->|5 | N2
    N8 -->|6 true| N7
    N8 -->|7 false| N6
    N9 -->|8 | N8
    N10 -->|9 | N2
    N11 -->|10 true| N10
    N11 -->|11 false| N9
    N12 -->|12 | N11
    N13 -->|13 | N2
    N14 -->|14 true| N13
    N14 -->|15 false| N12
    N15 -->|16 | N14
    N16 -->|17 | N2
    N17 -->|18 true| N16
    N17 -->|19 false| N15
    N18 -->|20 true| N17
    N18 -->|21 false| N15
    N19 -->|22 | N18
    N20 -->|23 | N18
    N21 -->|24 | N2
    N22 -->|25 true| N20
    N22 -->|26 false| N21
    N23 -->|27 true| N19
    N23 -->|28 false| N22
    N24 -->|29 | N23
    N25 -->|30 | N2
    N26 -->|31 true| N25
    N26 -->|32 false| N24
    N27 -->|33 | N26
    N29 -->|34 | N27
    N30 -->|35 | N29
    N28 -->|36 normal| N30
    N31 -->|37 | N2
    N28 -->|38 handled exception| N31
    N32 -->|39 | N2
    N33 -->|40 true| N32
    N33 -->|41 false| N28
    N34 -->|42 | N33
    N35 -->|43 | N2
    N36 -->|44 true| N35
    N36 -->|45 false| N34
    N37 -->|46 | N36
    N38 -->|47 | N37
    N39 -->|48 | N38
    N40 -->|49 | N39
    N42 -->|50 | N40
    N41 -->|51 normal| N42
    N43 -->|52 | N2
    N41 -->|53 handled exception| N43
    N44 -->|54 | N2
    N45 -->|55 true| N44
    N45 -->|56 false| N41
    N46 -->|57 | N45
    N47 -->|58 | N2
    N48 -->|59 true| N47
    N48 -->|60 false| N46
    N50 -->|61 | N48
    N49 -->|62 normal| N50
    N51 -->|63 | N2
    N49 -->|64 handled exception| N51
    N52 -->|65 true| N49
    N52 -->|66 false| N48
    N53 -->|67 | N52
    N54 -->|68 | N2
    N55 -->|69 true| N54
    N55 -->|70 false| N53
    N56 -->|71 | N2
    N57 -->|72 true| N56
    N57 -->|73 false| N55
    N58 -->|74 | N2
    N59 -->|75 true| N58
    N59 -->|76 false| N57
    N60 -->|77 | N2
    N61 -->|78 true| N60
    N61 -->|79 false| N59
    N62 -->|80 | N61
    N63 -->|81 | N2
    N64 -->|82 true| N63
    N64 -->|83 false| N62
    N65 -->|84 | N2
    N66 -->|85 true| N65
    N66 -->|86 false| N64
    N67 -->|87 | N66
    N68 -->|88 | N67
    N1 -->|89 | N68
```
