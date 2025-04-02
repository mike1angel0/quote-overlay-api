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
    author = data.get('author', '')

    try:
        response = requests.get(image_url)
        bg = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to load image from URL. {str(e)}"}, 400

    bg = bg.resize((1080, 1080))
    draw = ImageDraw.Draw(bg)

    try:
        font_quote = ImageFont.truetype("DejaVuSans.ttf", 48)
        font_author = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        font_quote = font_author = ImageFont.load_default()

    # Word wrapping for quote
    max_width = 900
    lines = []
    words = quote.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font_quote)
        test_width = bbox[2] - bbox[0]
        if test_width <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    # Estimate total text height (quote + spacing + author)
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h + 10

    if author:
        bbox_author = draw.textbbox((0, 0), author, font=font_author)
        author_height = bbox_author[3] - bbox_author[1]
        total_height += author_height + 10  # spacing before author
    else:
        author_height = 0

    # Draw semi-transparent background rectangle
    rect_y = 800
    rect = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    rect_draw = ImageDraw.Draw(rect)
    rect_draw.rectangle(
        [(0, rect_y - 20), (1080, rect_y + total_height + 20)],
        fill=(0, 0, 0, 150)
    )
    bg = Image.alpha_composite(bg.convert("RGBA"), rect)

    # Draw text
    draw = ImageDraw.Draw(bg)
    y = rect_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (1080 - w) / 2
        draw.text((x + 2, y + 2), line, font=font_quote, fill="black")
        draw.text((x, y), line, font=font_quote, fill="white")
        y += h + 10

    if author:
        y += 10  # extra spacing before author
        bbox = draw.textbbox((0, 0), author, font=font_author)
        w = bbox[2] - bbox[0]
        x = (1080 - w) / 2
        draw.text((x + 2, y + 2), author, font=font_author, fill="black")
        draw.text((x, y), author, font=font_author, fill="white")

    output = BytesIO()
    bg.convert("RGB").save(output, format='JPEG')
    output.seek(0)
    return send_file(output, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run()
