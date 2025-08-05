# Getting Youtube Video contens (Subtitles)
from pytubefix import YouTube
import srt

#yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
#print(yt.captions['en'].generate_srt_captions())

# ...existing code...

def get_content_from_youtube(url):
   try:
      yt = YouTube(url)
      captions = yt.captions

      if yt.captions:
         caption = yt.captions['a.ja']  # 'ja' for Japanese subtitles
         if not caption:
            caption = yt.captions['a.en']
         if not caption:
            return None
         caption_srt = caption.generate_srt_captions()
         # SRTからインデックスと時刻を除去
         caption_parsed = srt.parse(caption_srt)
         print(caption_parsed)
         caption_text = "\n".join(f"{item.content}" for item in caption_parsed)

         return caption_text
   except:
      return None

caption_text = get_content_from_youtube("https://www.youtube.com/watch?v=leejdKAEA1A")
print(caption_text)


