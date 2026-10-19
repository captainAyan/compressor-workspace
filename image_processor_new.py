import io
import math
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageStat

class ImageProcessor:
    """Handles heavy IO, compression, rotation, resizing, and difference caching."""
    @staticmethod
    def process_image(file_path, rotation_angle, format_type, quality, optimize):
        try:
            with Image.open(file_path) as img:
                rotated = img.rotate(rotation_angle, expand=True)
                save_format = "JPEG" if format_type == "JPEG" else format_type

                print("save format", save_format)

                if save_format == "JPEG" and rotated.mode in ("RGBA", "P"):
                    img_to_save = rotated.convert("RGB")
                else:
                    img_to_save = rotated

                buffer = io.BytesIO()
                img_to_save.save(buffer, format=save_format, quality=quality, optimize=optimize)
                buffer.seek(0)

                return buffer, None

        except Exception as e:
            return None, e

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


