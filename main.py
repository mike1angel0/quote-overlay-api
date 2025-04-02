from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    image_url = data.get('image_url')
    quote = data.get('quote', '')

    # Download the image
    response = requests.get(image_url)
    bg = Image.open(BytesIO(response.content)).convert("RGB")
    bg = bg.resize((1080, 1080))

    # Draw text
    draw = ImageDraw.Draw(bg)
    font = ImageFont.load_default()

    # Word wrap
    max_width = 900
    lines = []
    words = quote.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    y = 800
    for line in lines:
        w, h = draw.textsize(line, font=font)
        draw.text(((1080 - w) / 2, y), line, fill="white", font=font)
        y += h + 10

    output = BytesIO()
    bg.save(output, format='JPEG')
    output.seek(0)
    return send_file(output, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run()