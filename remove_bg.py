# -*- coding:utf-8 -*-
# __author__ = 'Weilit'
import requests
import logging
import os

API_ENDPOINT = "https://api.remove.bg/v1.0/removebg"


class RemoveBg:
    '''
    调用api去除输入图片的背景
    '''
    def __init__(self, api_key, error_log_file):
        self.__api_key = api_key
        logging.basicConfig(filename=error_log_file,
                            format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                            datefmt  = '%Y-%m-%d %A %H:%M:%S')

    def run(self, str_img, file_save_dir, size='preview', type='auto', format='png', roi='0% 0% 100% 100%', str_bg_image=None):
        """
        size: preview 为预览模式，每个月有50张免费额度
        type: auto/person/product/car   注意：动漫图片无法检测
        roi: 人工使用矩形框出需要检测的部分，"x1px y1px x2px y2px" or "x1% y1% x2% y2%"
        """
        if self.__judge_source(str_img) == 1:
            self.remove_background_from_img_url(str_img, file_save_dir, size, type, format, roi, str_bg_image)
        elif self.__judge_source(str_img) == 2:
            self.remove_background_from_img_file(str_img, file_save_dir, size, type, format, roi, str_bg_image)
        else:
            logging.error("Unable to save %s due to image source error which is %s", file_save_dir, str_img)


    def remove_background_from_img_file(self, img_file_path, file_save_dir, size, type, format, roi, str_bg_image):
        img_file = open(img_file_path, 'rb')
        if not str_bg_image:
            response = requests.post(
                API_ENDPOINT,
                files={'image_file': img_file},     # image_file必须放在files下，不能放在data中
                data={'size': size,
                      'type': type,
                      'format': format,
                      'roi': roi},
                headers={'X-Api-Key': self.__api_key})
        else:
            if self.__judge_source(str_bg_image) == 1:
                response = requests.post(
                    API_ENDPOINT,
                    files={'image_file': img_file},
                    data={'size': size,
                          'type': type,
                          'format': format,
                          'roi': roi,
                          'bg_image_url': str_bg_image},
                    headers={'X-Api-Key': self.__api_key})
            elif self.__judge_source(str_bg_image) == 1:
                response = requests.post(
                    API_ENDPOINT,
                    files={'image_file': img_file,
                           'bg_image_file': str_bg_image},
                    data={'size': size,
                          'type': type,
                          'format': format,
                          'roi': roi},
                    headers={'X-Api-Key': self.__api_key})
            else:
                logging.error("Unable to save %s due to bg_image error which is %s", file_save_dir, str_bg_image)
                img_file.close()
                return

        if img_file_path.count('\\') > 0:
            file_name = img_file_path.split("\\")[-1].split(".")[0]
        else:
            file_name = img_file_path.split("/")[-1].split(".")[0]
        new_file_path = os.path.join(file_save_dir, file_name) + "_rm_bg." + format
        self.__output_file__(response, new_file_path)
        # Close original file
        img_file.close()

    def remove_background_from_img_url(self, img_url, file_save_dir, size, type, format, roi, str_bg_image):
        """
        Removes the background given an image URL and outputs the file as the given new file name.
        :param img_url: the URL to the image
        :param size: the size of the output image (regular = 0.25 MP, hd = 4 MP, 4k = up to 10 MP)
        :param file_save_dir: the new file name of the image with the background removed
        """
        if not str_bg_image:
            response = requests.post(
                API_ENDPOINT,
                data={'image_url': img_url,
                      'size': size,
                      'type': type,
                      'format': format,
                      'roi': roi},
                headers={'X-Api-Key': self.__api_key})
        else:
            if self.__judge_source(str_bg_image) == 1:
                response = requests.post(
                    API_ENDPOINT,
                    data={'image_url': img_url,
                          'size': size,
                          'type': type,
                          'format': format,
                          'roi': roi,
                          'bg_image_url': str_bg_image},
                    headers={'X-Api-Key': self.__api_key})
            elif self.__judge_source(str_bg_image) == 1:
                response = requests.post(
                    API_ENDPOINT,
                    files={'bg_image_file': str_bg_image},
                    data={'image_url': img_url,
                          'size': size,
                          'type': type,
                          'format': format,
                          'roi': roi},
                    headers={'X-Api-Key': self.__api_key})
            else:
                logging.error("Unable to save %s due to bg_image error which is %s", file_save_dir, str_bg_image)
                return

        file_name = img_url.split('/')[-1].split('.')[0] + "_rm_bg." + format
        new_file_path = os.path.join(file_save_dir, file_name)
        self.__output_file__(response, new_file_path)


    # def remove_background_from_base64_img(self, base64_img, size="regular", file_save_dir="no-bg.png"):
    #     """
    #     Removes the background given a base64 image string and outputs the file as the given new file name.
    #     :param base64_img: the base64 image string
    #     :param size: the size of the output image (regular = 0.25 MP, hd = 4 MP, 4k = up to 10 MP)
    #     :param file_save_dir: the new file name of the image with the background removed
    #     """
    #     response = requests.post(
    #         API_ENDPOINT,
    #         data={
    #             'image_file_b64': base64_img,
    #             'size': size
    #         },
    #         headers={'X-Api-Key': self.__api_key}
    #     )
    #     self.__output_file__(response, file_save_dir)

    def __output_file__(self, response, file_save_dir):
        # If successful, write out the file
        if response.status_code == requests.codes.ok:
            with open(file_save_dir, 'wb') as removed_bg_file:
                removed_bg_file.write(response.content)
        # Otherwise, print out the error
        else:
            error_reason = response.json()["errors"][0]["title"].lower()
            logging.error("Unable to save %s due to %s", file_save_dir, error_reason)

    def __judge_source(self, str):
        if (str.startswith("http")):
            return 1            # url
        if (str.count('/')>0 or str.count('\\')>0):
            return 2            # file
        return 0                # error


if __name__ == '__main__':
    api_key = 'iWgsewfSYZi7ZrxPCXBRi61R'
    remove_bg = RemoveBg(api_key, './error_log.txt')
    remove_bg.run(r'D:\code\11.jpg', r'D:\code', roi="300px 300px 900px 900px")
    # remove_bg.run('http://st2.depositphotos.com/1211250/11537/i/950/depositphotos_115371752-stock-photo-couple-in-love-and-vintage.jpg', r'D:\code')
