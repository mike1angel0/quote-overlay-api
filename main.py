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

    try:
        response = requests.get(image_url)
        bg = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to load image from URL. {str(e)}"}, 400

    bg = bg.resize((1080, 1080))
    draw = ImageDraw.Draw(bg)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 48)
    except:
        font = ImageFont.load_default()

    # Word wrapping
    max_width = 900
    lines = []
    words = quote.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        if test_width <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    # Estimate total text height
    line_heights = []
    total_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h + 10  # 10px line spacing

    # Coordinates for rectangle
    rect_y = 800
    rect_height = total_height
    rect = Image.new("RGBA", bg.size, (0, 0, 0, 0))  # Transparent image
    rect_draw = ImageDraw.Draw(rect)

    rect_draw.rectangle(
        [(0, rect_y - 20), (1080, rect_y + rect_height + 20)],
        fill=(0, 0, 0, 150)  # Semi-transparent black
    )
    bg = Image.alpha_composite(bg.convert("RGBA"), rect)

    # Draw text on top of rectangle
    draw = ImageDraw.Draw(bg)
    y = rect_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (1080 - w) / 2

        # Shadow
        draw.text((x + 2, y + 2), line, font=font, fill="black")
        # Main text
        draw.text((x, y), line, font=font, fill="white")

        y += h + 10

    output = BytesIO()
    bg.convert("RGB").save(output, format='JPEG')
    output.seek(0)
    return send_file(output, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run()
