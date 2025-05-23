from Db import CowDataAccess
from Db.Models import Cow

import tkinter as tk
from tkinter import messagebox

import paho.mqtt.client as mqtt

from colour import Color

# container that holds the entire ui
class UI:
    def __init__(self, master, cow_data_access):
        self.master = master
        self.cow_data_access = cow_data_access
        master.title("Cattle Feed Management System")
        master.geometry("800x600")
        self.column_width = 30
        self.base_color = Color(hue=0.6, saturation=0.5, luminance=0.55)

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        self.client_id = "cattle_feed_management_system"
        self.mqtt_broker = "484e831498dc44a1a9ba35c92a683dca.s1.eu.hivemq.cloud"
        self.mqtt_port = 8883
        self.mqtt_user = "hivemq.webclient.1747639899064"
        self.mqtt_pass = "8961ABCDbedfEGah,%<$"
        self.mqqt_topic = "rfid/card_scans"

        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_pass)
        self.mqtt_client.tls_set()
        
        try:
            self.mqtt_client.connect_async(self.mqtt_broker, self.mqtt_port)
            self.mqtt_client.loop_start()
        except Exception as e:
            # do love how easy it is to throw an error message
            messagebox.showerror("MQTT Connection Error", f"MQTT connection failed: {e}")
        
        self.column_label_frame = tk.Frame(master)
        self.column_label_frame.pack(side=tk.TOP, fill=tk.X) 

        self.tag_id_label = tk.Label(self.column_label_frame, text="Tag ID", anchor="w", width=self.column_width, borderwidth=2, relief=tk.GROOVE)
        self.tag_id_label.grid(row=0, column=0, sticky="ew")
        self.name_label = tk.Label(self.column_label_frame, text="Name", anchor="w", width=self.column_width, borderwidth=2, relief=tk.GROOVE)
        self.name_label.grid(row=0, column=1, sticky="ew")
        self.feed_time_label = tk.Label(self.column_label_frame, text="Feed Time", anchor="w", width=self.column_width, borderwidth=2, relief=tk.GROOVE)
        self.feed_time_label.grid(row=0, column=2, sticky="ew")
        self.actions_label = tk.Label(self.column_label_frame, text="Actions", anchor="w", width=self.column_width, borderwidth=2, relief=tk.GROOVE)
        self.actions_label.grid(row=0, column=3, columnspan=2, sticky="ew")

        
        self.cow_list = CowList(master, cow_data_access=self.cow_data_access, column_width=self.column_width, base_color= self.base_color)
        self.cow_list.set_cows(self.cow_data_access.get_all_cows())
        self.cow_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.mqqt_topic)
        pass

    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.topic} {msg.payload}")
        card_id = msg.payload.decode("utf-8")
        print(f"Card ID: {card_id}")
        cow = self.cow_data_access.get_cow_by_tag_id(card_id)
        if cow is None:
            AddCowDialog(self.master, self.cow_list, card_id, self.cow_data_access)
        else:
            self.mqtt_client.publish("feed/time", cow.feed_time)
            pass
    
    def on_disconnect(self, client, userdata, rc):
        pass


# big ol scrollable list of cow details
class CowList(tk.Frame):
    def __init__(self, master, cow_data_access, column_width, base_color, **kwargs):
        super().__init__(master, **kwargs)
        self.cows = []
        self.column_width = column_width
        self.base_color = base_color

        self.cow_data_access = cow_data_access

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # I hate scrolling so much
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.update_list()

    def update_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, cow in enumerate(self.cows):
            temp_color = self.base_color
            if i % 2 :
                temp_color = Color(hue=self.base_color.hue, saturation=max(0, self.base_color.saturation - 0.1), luminance=self.base_color.luminance)
            cow_details = CowDetails(cow=cow, master=self.scrollable_frame, cow_list=self, cow_data_access=self.cow_data_access, column_width=self.column_width, base_color=temp_color)
            cow_details.pack(fill="x", anchor="w")

    def set_cows(self, cows):
        self.cows = cows
        self.update_list()


class CowDetails(tk.Frame):
    def __init__(self, cow: Cow, cow_list, cow_data_access, column_width, master, base_color,**kwargs):
        super().__init__(master, **kwargs)
        self.cow = cow
        self.cow_list = cow_list
        self.cow_data_access = cow_data_access
        self.column_width = column_width
        self.base_color = base_color
        self.alt_color = Color(hue=(self.base_color.hue - 0.05), saturation=self.base_color.saturation, luminance=self.base_color.luminance)

        self.tag_id_label = tk.Label(self, text=f"Tag ID: {cow.tag_id}", anchor="w", borderwidth=2, width=self.column_width, bg=self.base_color.hex_l)
        self.tag_id_label.grid(row=0, column=0, sticky="ew")

        self.name_label = tk.Label(self, text=f"Name: {cow.name}", anchor="w", borderwidth=2, width=self.column_width, bg=self.alt_color.hex_l)
        self.name_label.grid(row=0, column=1, sticky="ew")

        self.feed_time_label = tk.Label(self, text=f"Feed Time: {cow.feed_time:.3g}s", anchor="w", borderwidth=2, width=self.column_width, bg=self.base_color.hex_l)
        self.feed_time_label.grid(row=0, column=2, sticky="ew")

        button_height = self.tag_id_label.winfo_reqheight()

        self.update_button = tk.Button(self, text="Update", command=self.update_cow, height=1, width=8, padx=0, pady=0)
        self.update_button.grid(row=0, column=3, sticky="ew")

        self.delete_button = tk.Button(self, text="Delete", command=self.delete_cow, height=1, width=8, padx=0, pady=0)
        self.delete_button.grid(row=0, column=4, sticky="ew")

        self.columnconfigure(0, weight=1)

    def update_cow(self):
        UpdateCowDialog(self.master, self.cow, cow_list=self.cow_list)
        print(f"Update button pressed for cow: {self.cow.tag_id}")

    def delete_cow(self):
        DeletCowDialog(self.master, self.cow, cow_list=self.cow_list, cow_data_access=self.cow_data_access)
        print(f"Delete button pressed for cow: {self.cow.tag_id}")


class UpdateCowDialog(tk.Toplevel):
    def __init__(self, master, cow, cow_list):
        super().__init__(master)
        self.cow = cow
        self.cow_list = cow_list
        self.title(f"Update Cow: {cow.name}")

        self.tag_id_label = tk.Label(self, text="Tag ID:")
        self.tag_id_label.grid(row=0, column=0)
        self.tag_id_entry = tk.Entry(self, width=50)
        self.tag_id_entry.insert(0, str(cow.tag_id))
        self.tag_id_entry.config(state="disabled")
        self.tag_id_entry.grid(row=0, column=1)

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.grid(row=1, column=0)
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.insert(0, str(cow.name))
        self.name_entry.grid(row=1, column=1)

        self.feed_time_label = tk.Label(self, text="Feed Time:")
        self.feed_time_label.grid(row=2, column=0)
        self.feed_time_entry = tk.Entry(self, width=50)
        self.feed_time_entry.insert(0, str(cow.feed_time))
        self.feed_time_entry.grid(row=2, column=1)

        self.save_button = tk.Button(self, text="Save", command=self.save)
        self.save_button.grid(row=3, column=0, columnspan=2)

    def save(self):
        print(f"Saving cow: {self.cow.tag_id}")
        self.cow.name = self.name_entry.get()
        self.cow.feed_time = int(self.feed_time_entry.get())
        self.cow.save()
        self.cow_list.update_list()
        self.destroy()

class DeletCowDialog(tk.Toplevel):
    def __init__(self, master, cow, cow_list, cow_data_access):
        super().__init__(master)
        self.cow = cow
        self.cow_list = cow_list
        self.cow_data_access = cow_data_access
        self.title(f"Delete Cow: {cow.name}")

        self.label = tk.Label(self, text=f"Are you sure you want to delete {cow.name}?")
        self.label.pack()

        self.delete_button = tk.Button(self, text="Delete", command=self.delete)
        self.delete_button.pack()

    def delete(self):
        print(f"Deleting cow: {self.cow.tag_id}")
        self.cow.delete_instance()
        self.cow_list.set_cows(self.cow_data_access.get_all_cows())
        self.destroy()

class AddCowDialog(tk.Toplevel):
    def __init__(self, master, cow_list, tag_id, cow_data_access):
        super().__init__(master)
        self.cow_list = cow_list
        self.cow_data_access = cow_data_access
        self.title("New id tag scanned")

        self.title_label = tk.Label(self, text="Add New Cow")
        self.title_label.grid(row=0, column=0, columnspan=2)

        self.tag_id_label = tk.Label(self, text="Tag ID:")
        self.tag_id_label.grid(row=1, column=0)
        self.tag_id_entry = tk.Entry(self, width=50)
        self.tag_id_entry.insert(0, tag_id)
        self.tag_id_entry.config(state="disabled")
        self.tag_id_entry.grid(row=1, column=1)

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.grid(row=2, column=0)
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.grid(row=2, column=1)

        self.feed_time_label = tk.Label(self, text="Feed Time:")
        self.feed_time_label.grid(row=3, column=0)
        self.feed_time_entry = tk.Entry(self, width=50)
        self.feed_time_entry.grid(row=3, column=1)

        self.save_button = tk.Button(self, text="Add", command=self.add)
        self.save_button.grid(row=4, column=0, columnspan=2)

    def add(self):
        print(f"Adding new cow: {self.tag_id_entry.get()}")
        cow = Cow(
            tag_id=str(self.tag_id_entry.get()), 
            name=str(self.name_entry.get()), 
            feed_time=int(self.feed_time_entry.get())
        )

        cow.save()
        
        self.cow_list.after(0, self.cow_list.set_cows, self.cow_data_access.get_all_cows())
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ui = UI(root, CowDataAccess())
    root.mainloop()
