import io
import math
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageStat

class ImageProcessor:
    @staticmethod
    def process_image(file_path, only_compress, rotation_angle=0, format=None, quality=None, optimize=False):
        try:
            with Image.open(file_path) as img:
                rotated = img.rotate(rotation_angle, expand=True)

                save_format = format if format else (img.format if img.format else "JPEG")
                save_format = "JPEG" if save_format.upper() == "JPEG" else save_format

                # Handle color mode conversion for JPEG
                if save_format == "JPEG" and rotated.mode in ("RGBA", "P", "LA"):
                    image_to_save = rotated.convert("RGB")
                else:
                    image_to_save = rotated

                compressed_image_buffer = io.BytesIO()

                # Build save arguments dynamically
                save_kwargs = {}
                if quality is not None: save_kwargs["quality"] = quality
                if optimize: save_kwargs["optimize"] = optimize

                image_to_save.save(compressed_image_buffer, format=save_format, **save_kwargs)
                compressed_image_buffer.seek(0)

                # Calculating difference (for heatmap), psnr and ssim

                compressed_image = Image.open(compressed_image_buffer).copy()

                if only_compress:
                    return None, compressed_image_buffer, compressed_image, None, None, None

                else:
                    # Compute and cache raw grayscale difference for instant multiplier updates
                    original_image_rgb = rotated.convert("RGB")
                    compressed_image_rgb = compressed_image.convert("RGB")
                    if compressed_image_rgb.size != original_image_rgb.size:
                        compressed_image_rgb = compressed_image_rgb.resize(orig_rgb.size, Image.Resampling.BILINEAR)

                    difference_image = ImageChops.difference(original_image_rgb, compressed_image_rgb).convert("L")

                    # Calculate PSNR and SSIM metrics
                    psnr, ssim = ImageProcessor.calculate_metrics(original_image_rgb, compressed_image_rgb)
                    print("psnr", psnr)
                    print("ssim", ssim)

                    return None, compressed_image_buffer, compressed_image, difference_image, psnr, ssim

        except Exception as e:
            return e, None, None, None, None, None

    @staticmethod
    def calculate_metrics(orig_rgb, comp_rgb):
        # 1. PSNR Calculation
        diff = ImageChops.difference(orig_rgb, comp_rgb)
        stat = ImageStat.Stat(diff)
        mse = sum(r**2 for r in stat.rms) / len(stat.rms)
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * math.log10(255.0 / math.sqrt(mse))

        # 2. SSIM Calculation (Global structural similarity via NumPy)
        arr_orig = np.array(orig_rgb, dtype=np.float64)
        arr_comp = np.array(comp_rgb, dtype=np.float64)

        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        mu1 = arr_orig.mean()
        mu2 = arr_comp.mean()
        sigma1_sq = arr_orig.var()
        sigma2_sq = arr_comp.var()
        sigma12 = np.mean((arr_orig - mu1) * (arr_comp - mu2))

        ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
        return psnr, ssim

    @staticmethod
    def render_heatmap(raw_diff_gray, multiplier):
        enhancer = ImageEnhance.Brightness(raw_diff_gray)
        amplified = enhancer.enhance(multiplier)
        zero_channel = Image.new("L", amplified.size, 0)
        return Image.merge("RGB", (amplified, zero_channel, zero_channel))


