from PIL import Image, ImageDraw, ImageFont, ImageOps


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_title(draw, title, font, image_width, y, color, shadow_color):
    title_width, title_height = get_text_size(draw, title, font)
    x = (image_width - title_width) // 2

    shadow_offset = 2
    draw.text((x + shadow_offset, y + shadow_offset), title, font=font, fill=shadow_color)
    draw.text((x, y), title, font=font, fill=color)

    underline_y = y + title_height + 10
    draw.line((x, underline_y, x + title_width, underline_y), fill=color, width=2)

    return underline_y + 20


def draw_description(draw, description, font, x, y, image_width, color, shadow_color):
    lines = description.splitlines()
    bullet_indent = 20
    line_spacing = 10

    for line in lines:
        is_bullet = line.startswith("*  ")
        text = line[3:] if is_bullet else line  # Remove bullet prefix for measuring

        words = text.split()
        current_line = ""
        line_height = get_text_size(draw, "A", font)[1]

        # Set initial x based on bullet or normal line
        x_offset = x + bullet_indent if is_bullet else x
        prefix = "*  " if is_bullet else ""

        for word in words:
            test_line = f"{prefix}{current_line} {word}".strip()
            text_width, _ = get_text_size(draw, test_line, font)
            if text_width <= image_width - 2 * x:
                current_line = test_line
            else:
                draw.text((x_offset + 2, y + 2), current_line, font=font, fill=shadow_color)
                draw.text((x_offset, y), current_line, font=font, fill=color)
                y += line_height + line_spacing
                current_line = word
                prefix = ""  # Bullet symbol only for the first line of a bullet

        if current_line:
            draw.text((x_offset + 2, y + 2), current_line, font=font, fill=shadow_color)
            draw.text((x_offset, y), current_line, font=font, fill=color)
            y += line_height + line_spacing

    return y


def draw_code(draw, code, font, x, y, image_width, color, image_height, logo_img, margin, padding):
    lines = code.splitlines()
    outer_border = 2
    line_height = max(get_text_size(draw, line, font)[1] for line in lines)

    bottom_y = image_height - margin
    block_width = image_width - 2 * x
    block_height = bottom_y - y

    # Outer white border
    draw.rectangle(
        [x - outer_border, y - outer_border, x + block_width + outer_border, y + block_height + outer_border],
        fill="white"
    )

    # Inner black background
    draw.rectangle(
        [x, y, x + block_width, y + block_height],
        fill="black"
    )

    # Space reserved for logo at bottom-right
    logo_height = logo_img.height if logo_img else 0
    text_area_height = block_height - logo_height - padding

    y_text = y + padding
    x_text = x + padding

    for line in lines:
        if y_text + line_height <= y + text_area_height:
            draw.text((x_text, y_text), line, font=font, fill=color)
            y_text += line_height + 5
        else:
            break

    # Draw logo at bottom-right (with 5px padding from edges of code section)
    if logo_img:
        logo_x = x + block_width - logo_img.width - 5
        logo_y = y + block_height - logo_img.height - 5
        return (y + block_height + outer_border, logo_x, logo_y)

    return y + block_height + outer_border, None, None


def calculate_content_height(draw, post, title_font, desc_font, code_font, image_width, margin, logo_height):
    height = 0
    title_width, title_height = get_text_size(draw, post['title'], title_font)
    height += title_height + 10 + 4

    for line in post['description'].splitlines():
        _, line_height = get_text_size(draw, line, desc_font)
        height += line_height + 10

    height += 20 + 10
    height += 300 + logo_height + margin * 2

    return height


def create_image(post):
    content_width = 800
    margin = 40
    logo_size = 80
    border_width = 10
    padding = 20

    bg_color = "#00A79D"
    text_color = "white"
    code_text_color = "white"
    border_color = "white"
    title_shadow_color = (17, 124, 113)
    description_shadow_color = (16, 155, 142)

    temp_image = Image.new('RGB', (100, 100))
    draw_temp = ImageDraw.Draw(temp_image)
    title_font = ImageFont.truetype("fonts/Montserrat/static/Montserrat-Bold.ttf", 22)
    description_font = ImageFont.truetype("fonts/Montserrat/static/Montserrat-SemiBold.ttf", 16)
    code_font = ImageFont.truetype("fonts/Fira_Code/FiraCode-VariableFont_wght.ttf", 16)

    try:
        logo_img = Image.open("logo.png").convert("RGBA")
        logo_img = logo_img.resize((logo_size, logo_size))
    except FileNotFoundError:
        print("Logo image not found. Proceeding without it.")
        logo_img = None
        logo_size = 0

    content_height = calculate_content_height(draw_temp, post, title_font, description_font, code_font, content_width, margin, logo_size)
    image_size = (content_width + 2 * margin, content_height + 2 * margin)
    image = Image.new('RGB', image_size, color=bg_color)
    draw = ImageDraw.Draw(image)

    y = margin
    x_padding = margin

    y = draw_title(draw, post['title'], title_font, image_size[0], y, text_color, title_shadow_color)
    y = draw_description(draw, post['description'], description_font, x_padding, y, image_size[0], text_color, description_shadow_color)
    y += 20

    y, logo_x, logo_y = draw_code(draw, post['code'], code_font, x_padding, y, image_size[0], code_text_color, image_size[1], logo_img, margin, padding)

    if logo_img and logo_x is not None:
        image.paste(logo_img, (logo_x, logo_y), logo_img)

    final_image = image.convert("RGB")
    bordered_image = ImageOps.expand(final_image, border=border_width, fill=border_color)
    bordered_image.save('post.png')
    bordered_image.show()

