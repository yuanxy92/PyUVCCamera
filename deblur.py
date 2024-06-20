import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy

# 读取彩色图像
img = cv2.imread('./testsets/0619/camera_4_frame_228.jpg', cv2.IMREAD_COLOR)
# img = cv2.imread('./testsets/0619/camera_0_frame_72.jpg', cv2.IMREAD_COLOR)

# 将彩色图像转换为灰度图像
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 傅里叶变换
f_img = np.fft.fft2(gray_img)
f_img_shifted = np.fft.fftshift(f_img)

# 计算幅度谱
magnitude_spectrum = 20 * np.log(np.abs(f_img_shifted))

# 显示原始图像和频域图像
plt.figure(figsize=(12, 6))

plt.subplot(121)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image')
plt.axis('off')

plt.subplot(122)
plt.imshow(magnitude_spectrum, cmap='gray')
plt.title('Magnitude Spectrum')
plt.axis('off')

plt.show()


f_img_shifted_lowpass = copy.deepcopy(f_img_shifted)
crop_size1 = 40
crop_size2 = 100
f_img_shifted_lowpass_amp = np.abs(f_img_shifted_lowpass)
f_img_shifted_lowpass_phase = np.angle(f_img_shifted_lowpass)
# f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,100-crop_size1:100+crop_size1]=f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,100-crop_size1:100+crop_size1]*1e-8
# f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,300-crop_size1:300+crop_size1]=f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,300-crop_size1:300+crop_size1]*1e-8

for c in range(-crop_size1,crop_size1+1):
    weight = abs(c)/crop_size1 * (1-1e-8) + 1e-8
    f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,100-c:100-c+1]=f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,100-c:100-c+1]*weight
    f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,300-c:300-c+1]=f_img_shifted_lowpass_amp[200-crop_size2:200+crop_size2,300-c:300-c+1]*weight


f_img_shifted_lowpass = f_img_shifted_lowpass_amp * (np.cos(f_img_shifted_lowpass_phase) + 1j * np.sin(f_img_shifted_lowpass_phase))

magnitude_spectrum_lowpass = 20 * np.log(np.abs(f_img_shifted_lowpass))

f_img_lowpass = np.fft.ifftshift(f_img_shifted_lowpass)
img_lowpass = np.fft.ifft2(f_img_lowpass)
img_filtered = np.abs(img_lowpass)

# 归一化处理
img_filtered_normalized = (img_filtered - np.min(img_filtered)) / (np.max(img_filtered) - np.min(img_filtered)) * 255
img_filtered_normalized = img_filtered_normalized.astype(np.uint8)

# 显示原始图像、幅度谱和处理后的图像
plt.figure(figsize=(12, 8))

plt.subplot(131)
plt.imshow(gray_img, cmap='gray')
plt.title('Original Image')
plt.axis('off')

plt.subplot(132)
plt.imshow(magnitude_spectrum_lowpass, cmap='gray')
plt.title('Magnitude Spectrum')
plt.axis('off')

plt.subplot(133)
plt.imshow(img_filtered_normalized, cmap='gray')
plt.title('Filtered Image (Normalized)')
plt.axis('off')

plt.show()