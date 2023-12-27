import os
import requests
import title
import logging


def get_image(soup, current_date):
    try:
        div_tag = soup.find('div', {'class': 'story__content'})
        if div_tag is None:
            return None  # Return None if the div tag is not found

        img_tag = div_tag.find('img')
        if img_tag is None:
            return None  # Return None if the img tag is not found

        img_url = img_tag['src']
        response_img = requests.get(img_url)
        base_directory = os.path.dirname(os.path.abspath(__file__))
        project_directory = os.path.join(base_directory)
        date = current_date.split('-')
        image_name = title.get_title(soup).strip() + '.jpeg'
        image_path = project_directory + '/' + 'data' + '/' + date[0] + '/' + date[1] + '/' + date[2] + '/' + 'images' + '/' + image_name
        with open(image_path, 'wb') as f:
            f.write(response_img.content)
        return image_path
    except Exception as excep:
        logging.info('%s - %s', "EXCEPTION IN GET IMAGE FUNCTION", excep)
