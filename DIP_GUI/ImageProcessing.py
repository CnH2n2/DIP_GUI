import cv2 as cv
import numpy as np

class DIP(object):
    def __init__(self):
        super(DIP, self).__init__()


    def addGaussNoise(self,img, mean=0, sigma=0.05):
        # 将图片灰度标准化
        img = img / 255
        # 产生高斯噪声
        noise = np.random.normal(mean, sigma, img.shape)
        # 将噪声与图片叠加
        img_out = img + noise
        # 将图像的灰度级限制在0~255
        img_out = np.clip(img_out, 0, 1)
        img_out = np.uint8(img_out * 255)
        return img_out

    def addSalt_pepper(self,img, SNR=0.01):
        noise_img=np.copy(img)
        num_salt=np.ceil(SNR*img.size*0.5)
        coords=[np.random.randint(0,i-1,int(num_salt))for i in img.shape]
        noise_img[coords[0],coords[1],:]=[255,255,255]
        num_pepper=np.ceil(SNR*img.size*0.5)
        coords=[np.random.randint(0,i-1,int(num_pepper))for i in img.shape]
        noise_img[coords[0],coords[1],:]=[0,0,0]
        return noise_img

    def hist(self,img):
        b,g,r=cv.split(img)
        r1=cv.equalizeHist(r)
        g1=cv.equalizeHist(g)
        b1=cv.equalizeHist(b)
        img_equal_clo=cv.merge([b1,g1,r1])
        return img_equal_clo

    def log(self,img,c):
        img_log=c*np.log(1.0+img)
        img_log=np.uint8(img_log+0.5)
        return img_log

# img=cv.imread('Image/1.jpg')
# img=cv.resize(img,(500,500), interpolation=cv.INTER_AREA)
# # img=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
# cv.imshow('Original img',img)
# dip=DIP()
# img_blur=dip.log(img,70)
# cv.imshow('blur img',img_blur)
# cv.waitKey(0)
# cv.destroyAllWindows()