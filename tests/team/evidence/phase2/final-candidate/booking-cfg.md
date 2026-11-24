# Booking control-flow graph

`backend/routes/patient.py:213` through line 339. Each explicit return joins one exit. One decision is counted per condition, with an explicit handled-exception edge per handler. Uncaught runtime exceptions and framework decorators are outside the function CFG.

- Concrete graph: E = 91, N = 69, P = 1. M = **24**.
- Short-circuit variant: E = 101, N = 74, P = 1. M = **29**.

```mermaid
flowchart TD
    N1["1. entry"]
    N2["2. exit"]
    N3["3. L339 return jsonify({'success': True, 'message': 'Appointment booked successfully', 'da..."]
    N4["4. L337 return (jsonify({'success': False, 'message': SLOT_CONFLICT}), 400)"]
    N5["5. L336 not commit_appointment()"]
    N6["6. L335 db.session.add(appointment)"]
    N7["7. L326 appointment = Appointment(doctor_id=doctor_id, patient_id=patient.id, appointment_..."]
    N8["8. L323 return (jsonify({'success': False, 'message': 'You already have an appointment at ..."]
    N9["9. L322 patient_conflict"]
    N10["10. L315 patient_conflict = Appointment.query.filter_by(patient_id=patient.id, appointment_..."]
    N11["11. L312 return (jsonify({'success': False, 'message': 'This slot is already booked'}), 400)"]
    N12["12. L311 existing_booking"]
    N13["13. L304 existing_booking = Appointment.query.filter_by(doctor_id=doctor_id, appointment_da..."]
    N14["14. L301 return (jsonify({'success': False, 'message': f'Doctor is not available for {slot_..."]
    N15["15. L300 not availability"]
    N16["16. L293 availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, availabilit..."]
    N17["17. L290 return (jsonify({'success': False, 'message': f'Cannot book this slot for today as..."]
    N18["18. L289 current_hour >= hour"]
    N19["19. L288 apt_date == today"]
    N20["20. L281 slot_type = 'morning'"]
    N21["21. L283 slot_type = 'evening'"]
    N22["22. L285 return (jsonify({'success': False, 'message': 'Invalid time slot. Only Morning (09..."]
    N23["23. L282 15 <= hour < 19"]
    N24["24. L280 9 <= hour < 13"]
    N25["25. L279 hour = apt_time.hour"]
    N26["26. L276 return (jsonify({'success': False, 'message': 'Notes must be text'}), 400)"]
    N27["27. L275 notes is not None and (not isinstance(notes, str))"]
    N28["28. L274 notes = data.get('notes', '')"]
    N29["29. L268 try"]
    N30["30. L270 apt_time = datetime.strptime(start, '%H:%M').time()"]
    N31["31. L269 start = time_str.split('-', 1)[0].strip() if '-' in time_str else time_str"]
    N32["32. L272 return (jsonify({'success': False, 'message': 'Invalid appointment time format'}),..."]
    N33["33. L267 return (jsonify({'success': False, 'message': 'Invalid appointment time format'}),..."]
    N34["34. L266 not isinstance(time_str, str)"]
    N35["35. L265 time_str = data['appointment_time']"]
    N36["36. L262 return (jsonify({'success': False, 'message': 'Cannot book appointments for past d..."]
    N37["37. L261 apt_date < today"]
    N38["38. L259 current_minute = now.minute"]
    N39["39. L258 current_hour = now.hour"]
    N40["40. L257 today = now.date()"]
    N41["41. L256 now = datetime.utcnow() + timedelta(hours=5, minutes=30)"]
    N42["42. L249 try"]
    N43["43. L250 apt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()"]
    N44["44. L252 return (jsonify({'success': False, 'message': 'Invalid date format'}), 400)"]
    N45["45. L247 return (jsonify({'success': False, 'message': 'Doctor not found or inactive'}), 404)"]
    N46["46. L246 doctor is None or not doctor.is_active"]
    N47["47. L245 doctor = Doctor.query.get(doctor_id)"]
    N48["48. L243 return (jsonify({'success': False, 'message': 'Doctor ID must be an integer'}), 400)"]
    N49["49. L242 type(doctor_id) is not int or not -2 ** 63 <= doctor_id < 2 ** 63"]
    N50["50. L238 try"]
    N51["51. L239 doctor_id = int(doctor_id)"]
    N52["52. L241 return (jsonify({'success': False, 'message': 'Doctor ID must be an integer'}), 400)"]
    N53["53. L237 isinstance(doctor_id, str) and doctor_id.isascii() and doctor_id.isdecimal()"]
    N54["54. L236 doctor_id = data['doctor_id']"]
    N55["55. L234 return (jsonify({'success': False, 'message': 'Appointment time is required'}), 400)"]
    N56["56. L233 not data.get('appointment_time')"]
    N57["57. L231 return (jsonify({'success': False, 'message': 'Appointment date is required'}), 400)"]
    N58["58. L230 not data.get('appointment_date')"]
    N59["59. L228 return (jsonify({'success': False, 'message': 'Doctor ID is required'}), 400)"]
    N60["60. L227 not data.get('doctor_id')"]
    N61["61. L225 return (jsonify({'success': False, 'message': 'Booking requires a JSON object'}), ..."]
    N62["62. L224 not isinstance(data, dict)"]
    N63["63. L223 data = request.get_json(silent=True)"]
    N64["64. L221 return (jsonify({'success': False, 'message': 'Your account has been blacklisted. ..."]
    N65["65. L220 patient.is_blacklisted"]
    N66["66. L218 return (jsonify({'success': False, 'message': 'Patient profile not found'}), 404)"]
    N67["67. L217 patient is None"]
    N68["68. L215 patient = Patient.query.filter_by(user_id=user_id).first()"]
    N69["69. L214 user_id = get_current_user_id()"]
    N3 -->|1 | N2
    N4 -->|2 | N2
    N5 -->|3 true| N4
    N5 -->|4 false| N3
    N6 -->|5 | N5
    N7 -->|6 | N6
    N8 -->|7 | N2
    N9 -->|8 true| N8
    N9 -->|9 false| N7
    N10 -->|10 | N9
    N11 -->|11 | N2
    N12 -->|12 true| N11
    N12 -->|13 false| N10
    N13 -->|14 | N12
    N14 -->|15 | N2
    N15 -->|16 true| N14
    N15 -->|17 false| N13
    N16 -->|18 | N15
    N17 -->|19 | N2
    N18 -->|20 true| N17
    N18 -->|21 false| N16
    N19 -->|22 true| N18
    N19 -->|23 false| N16
    N20 -->|24 | N19
    N21 -->|25 | N19
    N22 -->|26 | N2
    N23 -->|27 true| N21
    N23 -->|28 false| N22
    N24 -->|29 true| N20
    N24 -->|30 false| N23
    N25 -->|31 | N24
    N26 -->|32 | N2
    N27 -->|33 true| N26
    N27 -->|34 false| N25
    N28 -->|35 | N27
    N30 -->|36 | N28
    N31 -->|37 | N30
    N29 -->|38 normal| N31
    N32 -->|39 | N2
    N29 -->|40 handled exception| N32
    N33 -->|41 | N2
    N34 -->|42 true| N33
    N34 -->|43 false| N29
    N35 -->|44 | N34
    N36 -->|45 | N2
    N37 -->|46 true| N36
    N37 -->|47 false| N35
    N38 -->|48 | N37
    N39 -->|49 | N38
    N40 -->|50 | N39
    N41 -->|51 | N40
    N43 -->|52 | N41
    N42 -->|53 normal| N43
    N44 -->|54 | N2
    N42 -->|55 handled exception| N44
    N45 -->|56 | N2
    N46 -->|57 true| N45
    N46 -->|58 false| N42
    N47 -->|59 | N46
    N48 -->|60 | N2
    N49 -->|61 true| N48
    N49 -->|62 false| N47
    N51 -->|63 | N49
    N50 -->|64 normal| N51
    N52 -->|65 | N2
    N50 -->|66 handled exception| N52
    N53 -->|67 true| N50
    N53 -->|68 false| N49
    N54 -->|69 | N53
    N55 -->|70 | N2
    N56 -->|71 true| N55
    N56 -->|72 false| N54
    N57 -->|73 | N2
    N58 -->|74 true| N57
    N58 -->|75 false| N56
    N59 -->|76 | N2
    N60 -->|77 true| N59
    N60 -->|78 false| N58
    N61 -->|79 | N2
    N62 -->|80 true| N61
    N62 -->|81 false| N60
    N63 -->|82 | N62
    N64 -->|83 | N2
    N65 -->|84 true| N64
    N65 -->|85 false| N63
    N66 -->|86 | N2
    N67 -->|87 true| N66
    N67 -->|88 false| N65
    N68 -->|89 | N67
    N69 -->|90 | N68
    N1 -->|91 | N69
```
