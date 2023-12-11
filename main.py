import os
from PIL import Image
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips,AudioFileClip,CompositeAudioClip
from gtts import gTTS

def resizeImages(folder_path, desired_size):
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for image_file in image_files:
        try:
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)
            resized_img = img.resize(desired_size)
            resized_img.save(os.path.join(folder_path, f'Modified_{image_file}'))
        except Exception as e:
            print(f"Error processing {image_file}: {str(e)}")

def textToSpeech(input_folder, output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            
            with open(input_path, "r") as file:
                text = file.read()

            tts = gTTS(text, lang='en')
            
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.mp3")
            tts.save(output_path)
            
            print(f"Conversion completed for: {filename}")

def imagesToVideo(image_folder, output_video,music_file,audio_folder,duration=5):
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg')) and f.startswith('Modified_')])
    audio_files = sorted([f for f in os.listdir(audio_folder) if f.endswith(('.mp3'))])

    clips = []
    counter=0
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        audio_path = os.path.join(audio_folder,audio_files[counter])

        audioScript=AudioFileClip(audio_path)
        duration=audioScript.duration
        audioScript = audioScript.volumex(2)
        clip = VideoFileClip(image_path).subclip(0, duration)
        clip=clip.set_audio(audioScript)
        clips.append(clip)
        counter+=1

    final_clip = concatenate_videoclips(clips, method="compose")

    bg_music = AudioFileClip(music_file)
    bg_music = bg_music.volumex(0.4) 

    final_audio = CompositeAudioClip([final_clip.audio, bg_music])
    final_clip = final_clip.set_audio(final_audio)

    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')

    for image_file in image_files:
        image_path = os.path.join(image_folder,image_file)
        os.remove(image_path)

    for audio_file in audio_files:
        audio_path = os.path.join(audio_folder,audio_file)
        os.remove(audio_path)


if __name__ == "__main__":
    folder_name = 'images'
    desired_size = (1920, 1080)
    resizeImages(folder_name, desired_size)
    textToSpeech('scripts', 'audioScripts')
    imagesToVideo('images','myVideo.mp4','./backgroundMusic/temp.mp3','audioScripts')
