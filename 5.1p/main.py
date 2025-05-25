import tkinter as tk
from gpiozero import LED

leds = [LED(17), LED(27), LED(22)]  

def main():

    def control_led(selected_led):
        for i, led in enumerate(leds):
            if i == selected_led:
                led.on()
            else:
                led.off()

    # these could be lamdas but for the sake of clarity they are not.
    def select_led_1():
        control_led(0)

    def select_led_2():
        control_led(1)

    def select_led_3():
        control_led(2)

    root = tk.Tk()
    root.title("LED Controller")

    selected_led = tk.IntVar(value=-1)

    # radio buttons
    tk.Radiobutton(root, text="LED 1", variable=selected_led, value=0, command=select_led_1).pack()
    tk.Radiobutton(root, text="LED 2", variable=selected_led, value=1, command=select_led_2).pack()
    tk.Radiobutton(root, text="LED 3", variable=selected_led, value=2, command=select_led_3).pack()

    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        for led in leds: # little bita cleanup
            led.off()
        print("\nAnd Away We Go!")
