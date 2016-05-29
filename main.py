# coding=utf-8
from __future__ import unicode_literals

import datetime as dt
import os

from PIL import Image, ImageDraw, ImageFont
from git import Repo, GitCommandError

from credentials import LOGIN, PASSWORD
from github_pixel_bot.settings import REPOSITORY_PATH, REPOSITORY_URL, FILE_TEMPLATE, COMMIT_MESSAGE

ASCII_CHARS = [' ', '%', 'S', '*', '@']


def map_pixels_to_ascii_chars(image, range_width=52):
    pixels_in_image = list(image.getdata())
    pixels_to_chars = [ASCII_CHARS[pixel_value / range_width] for pixel_value in pixels_in_image]
    return ''.join(pixels_to_chars)


def convert_image_to_ascii(message, new_width=51):
    width = 51
    height = 7
    image = Image.new('RGBA', (width, height))
    d = ImageDraw.Draw(image)

    fnt = ImageFont.truetype('fonts/pixel_font.ttf', 7)
    d.text((0, -1), message, font=fnt, fill=(255, 255, 255, 128))
    # image.show()
    # image = scale_image(image, new_width)
    # image.thumbnail((51, 7), Image.NEAREST)
    # image.show()

    image = image.convert('L')

    pixels_to_chars = map_pixels_to_ascii_chars(image)
    len_pixels_to_chars = len(pixels_to_chars)

    image_ascii = [pixels_to_chars[index: index + new_width] for index in
                   range(0, len_pixels_to_chars, new_width)]

    return image_ascii


def print_ascii(ascii):
    for line in ascii:
        print(line)


def convert_ascii_to_datetime_list(ascii):
    """Гитхаб отображается 53 недели, 2 из которых могут быть неполными"""
    now = dt.datetime.today()
    last_year_sunday = now - dt.timedelta(days=now.weekday() + 1, weeks=51)
    commit_datetimes = list()
    for line_index in range(len(ascii)):
        line = ascii[line_index]
        for i in range(len(line)):
            if line[i] != ' ':
                commit_datetimes.append(last_year_sunday + dt.timedelta(days=i * 7 + line_index))
    commit_datetimes.sort()
    return commit_datetimes


def main():
    message = dt.datetime.now().strftime("%H : %M : %S")
    ascii = convert_image_to_ascii(message=message)
    print_ascii(ascii)
    datetimes = convert_ascii_to_datetime_list(ascii)
    try:
        repo = (Repo
                .clone_from('http://{login}:{password}@{url}'
                            .format(login=LOGIN, password=PASSWORD, url=REPOSITORY_URL),
                            REPOSITORY_PATH)
                )
    except GitCommandError as e:
        repo = Repo(REPOSITORY_PATH)
    file_name = FILE_TEMPLATE.format(
        commit_message=COMMIT_MESSAGE,
        date=dt.datetime.now().strftime('%m.%d %H:%M')
    )

    for commit_datetime in datetimes:
        with open(os.path.join(REPOSITORY_PATH, file_name), 'w') as f:
            f.write(str(dt.datetime.now()))
        repo.git.add(file_name)
        print(commit_datetime)
        print(repo.git.commit(
            date=commit_datetime.strftime('%a %b %d %H:%M:%S %Y %z'),
            message=COMMIT_MESSAGE,
            author='GithubWriteBot <ioncheg@yandex.ru>',
        ))
    repo.git.push()


if __name__ == '__main__':
    main()
