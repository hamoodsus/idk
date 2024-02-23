import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import openai
import requests
from io import BytesIO
import threading
import cv2
import pygame
import os

# Set your OpenAI API key here
openai.api_key = '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'

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        master.title("Chatbot App")

        # Set initial theme (light mode)
        self.dark_mode = False

        # Set background image from URL
        image_url = "https://i.ibb.co/RgMTv7F/R-1.jpg"  # Replace with your image URL
        original_image = self.load_image_from_url(image_url)

        # Resize the image to match the screen dimensions
        resized_image = original_image.resize((self.master.winfo_screenwidth(), self.master.winfo_screenheight()))

        # Convert the resized image to PhotoImage
        self.background_image = ImageTk.PhotoImage(resized_image)

        # Create a canvas and pack it to fill the entire window
        self.canvas = tk.Canvas(master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())
        self.canvas.pack()

        # Create the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        # Load and play video in a separate thread
        self.video_thread = threading.Thread(target=self.load_and_play_video)
        self.video_thread.start()

    def load_and_play_video(self):
        # Video URL
        video_url = "https://cdn.discordapp.com/attachments/1188506289358250004/1210598796699111505/Link_Start___Sword_Art_Online_SFX_Only_No_Voices_1_1.mp4?ex=65eb24fc&is=65d8affc&hm=44171303cfbd991e16547ad6b80c59c2f6a19f0cceffdb8707daf21b51507e07&"  # Replace with your video URL

        # Fetch video content from URL
        response = requests.get(video_url)
        if response.status_code == 200:
            # Create a temporary file to write video content
            temp_file_path = "temp_video.mp4"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(response.content)

            # Initialize pygame
            pygame.init()

            # Get screen width and height
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

            # Load the video
            pygame.mixer.quit()  # Disable sound
            video = cv2.VideoCapture(temp_file_path)

            # Get the dimensions of the video
            video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            while True:
                ret, frame = video.read()
                if not ret:
                    break

                # Resize the frame to fit the screen
                frame = cv2.resize(frame, (screen_width, screen_height))

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.image.frombuffer(frame.tostring(), (screen_width, screen_height), "RGB")
                screen.blit(frame, (0, 0))
                pygame.display.flip()

            # Release video capture and close Pygame
            video.release()
            pygame.quit()

            # Delete the temporary file
            os.remove(temp_file_path)

            # Create a transparent frame for the chat
            self.chat_frame = tk.Frame(self.master)  # Transparent background
            self.chat_frame.place(relx=0.5, rely=0.5, anchor="center")

            # Configure the transparency level for the entire window
            self.master.attributes('-alpha', 0.9)  # Set transparency level

            # Create scrolled text for chat history
            self.chat_history = scrolledtext.ScrolledText(
                self.chat_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 12), bd=0, bg="white", padx=10, pady=10
            )
            self.chat_history.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

            # Create entry for user input
            self.user_input_entry = tk.Entry(self.chat_frame, width=50, font=("Arial", 12), bd=0, bg="white")
            self.user_input_entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            # Create "Send" button
            self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message, bd=0, bg="#0084FF", fg="white")
            self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

            # Create a button to toggle dark mode
            self.dark_mode_button = tk.Button(self.master, text="Dark Mode", command=self.toggle_dark_mode, bd=0, bg="#0084FF", fg="white")
            self.dark_mode_button.pack(side=tk.BOTTOM, pady=10)

            # Perform initial chat with OpenAI
            self.chat_with_openai("")

        else:
            print("Failed to fetch video from URL.")

    def load_image_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            return img
        except requests.exceptions.RequestException as e:
            print(f"Error loading image from URL: {e}")
            return None
        except PIL.UnidentifiedImageError as e:
            print(f"Error identifying image file: {e}")
            return None

    def send_message(self):
        user_input = self.user_input_entry.get()
        self.update_chat_history(f"You: {user_input}")
        self.chat_with_openai(user_input)
        self.user_input_entry.delete(0, tk.END)

    def chat_with_openai(self, user_input):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        chatbot_response = response['choices'][0]['message']['content']
        self.update_chat_history(f"Chatbot: {chatbot_response}")

    def update_chat_history(self, message):
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.see(tk.END)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.master.configure(bg="#1E1E1E")
            self.user_input_entry.configure(bg="#333333", fg="white")
            self.send_button.configure(bg="#333333", fg="white")
            self.dark_mode_button.configure(bg="#333333", fg="white")
        else:
            self.master.configure(bg="white")
            self.user_input_entry.configure(bg="white", fg="black")
            self.send_button.configure(bg="#0084FF", fg="white")
            self.dark_mode_button.configure(bg="#0084FF", fg="white")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()