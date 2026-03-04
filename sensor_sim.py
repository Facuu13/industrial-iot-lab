import time

def main():
    motor_on = 0
    speed_ok = 0
    temp_ok = 1
    fault_mech = False
    fault_temp = False
    last_slot = -1

    while True:
        
        # si motor on y no hay falla mecánica, speed_ok = 1
        if motor_on and not fault_mech:
            speed_ok = 1
        elif motor_on and fault_mech:
            speed_ok = 0
        else:
            speed_ok = 0

        #Temperatura, si no hay falla de temperatura, temp_ok = 1
        if not fault_temp:
            temp_ok = 1
        else:            
            temp_ok = 0


        data = {
            "ts": round(time.time(), 3),
            "motor_on": motor_on,
            "speed_ok": speed_ok,
            "temp_ok": temp_ok,
            "fault_mech": fault_mech,
            "fault_temp": fault_temp
        }

        print(data)
        time.sleep(0.5)

        slot = int(time.time()) // 5
        # cada ~5 segundos te pregunto si querés toggle motor
        if slot != last_slot:
            last_slot = slot
            cmd = input("cmd (m=toggle motor, fm=toggle fault mecánica, ft=toggle fault temperatura, q=quit, enter=skip): ").strip().lower()
            if cmd == "m":
                motor_on = 0 if motor_on else 1
            elif cmd == "fm":
                fault_mech = not fault_mech
            elif cmd == "ft":
                fault_temp = not fault_temp
            elif cmd == "q":
                break

if __name__ == "__main__":
    main()