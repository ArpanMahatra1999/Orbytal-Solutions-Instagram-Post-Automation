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

def draw_description(draw, description, font, x, y, image_width, color, shadow_color, max_height):
    lines = description.splitlines()
    prev_line_was_bullet = False

    for line in lines:
        if y >= max_height:
            break

        is_bullet_point = line.startswith("*  ")
        if prev_line_was_bullet and not is_bullet_point:
            y += 10

        if is_bullet_point:
            draw.text((x, y), line, font=font, fill=shadow_color)
            draw.text((x, y), line, font=font, fill=color)
            _, line_height = get_text_size(draw, line, font)
            y += line_height + 10
        else:
            words = line.split()
            current_line = ""
            line_height = get_text_size(draw, "A", font)[1]

            for word in words:
                if get_text_size(draw, current_line + " " + word, font)[0] <= image_width - x * 2:
                    current_line += " " + word if current_line else word
                else:
                    if y + line_height > max_height:
                        break
                    draw.text((x + 2, y + 2), current_line, font=font, fill=shadow_color)
                    draw.text((x, y), current_line, font=font, fill=color)
                    y += line_height + 10
                    current_line = word

            if current_line and y + line_height <= max_height:
                draw.text((x + 2, y + 2), current_line, font=font, fill=shadow_color)
                draw.text((x, y), current_line, font=font, fill=color)
                y += line_height + 10

        prev_line_was_bullet = is_bullet_point

    return y

def draw_code(draw, code, font, x, y, image_width, color, image_height, logo_img, margin, padding):
    lines = code.splitlines()
    outer_border = 2
    line_height = max(get_text_size(draw, line, font)[1] for line in lines)

    bottom_y = image_height - margin
    block_width = image_width - 2 * x
    block_height = bottom_y - y

    draw.rectangle(
        [x - outer_border, y - outer_border, x + block_width + outer_border, y + block_height + outer_border],
        fill="white"
    )

    draw.rectangle(
        [x, y, x + block_width, y + block_height],
        fill="black"
    )

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

    if logo_img:
        logo_x = x + block_width - logo_img.width - 5
        logo_y = y + block_height - logo_img.height - 5
        return (y + block_height + outer_border, logo_x, logo_y)

    return y + block_height + outer_border, None, None

def create_image(post):
    fixed_size = (800, 800)
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

    temp_image = Image.new('RGB', fixed_size)
    draw_temp = ImageDraw.Draw(temp_image)
    title_font = ImageFont.truetype("fonts/Montserrat/static/Montserrat-Bold.ttf", 25)
    description_font = ImageFont.truetype("fonts/Montserrat/static/Montserrat-SemiBold.ttf", 18)
    code_font = ImageFont.truetype("fonts/Fira_Code/FiraCode-VariableFont_wght.ttf", 18)

    try:
        logo_img = Image.open("logo.png").convert("RGBA")
        logo_img = logo_img.resize((logo_size, logo_size))
    except FileNotFoundError:
        print("Logo image not found. Proceeding without it.")
        logo_img = None
        logo_size = 0

    working_image = Image.new("RGB", (1000, 2000), color=bg_color)
    draw = ImageDraw.Draw(working_image)

    x_padding = margin
    y = margin

    y = draw_title(draw, post['title'], title_font, working_image.width, y, text_color, title_shadow_color)

    max_description_y = fixed_size[1] - 300  # Leave room for code box
    y = draw_description(draw, post['description'], description_font, x_padding, y, working_image.width, text_color, description_shadow_color, max_description_y)

    y += 20
    y, logo_x, logo_y = draw_code(draw, post['code'], code_font, x_padding, y, working_image.width, code_text_color, working_image.height, logo_img, margin, padding)

    if logo_img and logo_x is not None:
        working_image.paste(logo_img, (logo_x, logo_y), logo_img)

    cropped_image = working_image.crop((0, 0, fixed_size[0], fixed_size[1]))
    bordered_image = ImageOps.expand(cropped_image, border=border_width, fill=border_color)
    bordered_image.save("post.png")
    bordered_image.show()
