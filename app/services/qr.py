import qrcode
from qrcode.image.svg import SvgPathImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import io
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional


class QRService:
    """Service for generating QR codes"""
    
    @staticmethod
    def generate_qr_png(data: str, filename: str = None, size: int = 300, 
                       logo_text: str = None, style: str = "standard",
                       color: str = "#000000") -> str:
        """Generate QR code as PNG file and return filename"""
        base_path = 'app/static/qr'
        Path(base_path).mkdir(parents=True, exist_ok=True)
        
        # Calculate box_size based on desired pixel size
        box_size = max(1, size // 50)  # Roughly 50 modules per QR code
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Generate styled QR code if style is specified
        if style == "thai" and color != "#000000":
            # Use styled image with color
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(color)
            )
        else:
            # Standard QR code
            img = qr.make_image(fill_color=color, back_color="white")
        
        # Add logo text if provided
        if logo_text:
            img = QRService._add_text_to_qr(img, logo_text)
        
        # Save to file
        if not filename:
            filename = f"qr_{hash(data) % 10000}.png"
        
        file_path = os.path.join(base_path, filename)
        img.save(file_path, 'PNG', optimize=True, quality=95)
        
        return filename
    
    @staticmethod
    def _add_text_to_qr(qr_img: Image.Image, text: str) -> Image.Image:
        """Add text below QR code"""
        try:
            # Create new image with space for text
            margin = 60
            new_height = qr_img.height + margin
            new_img = Image.new('RGB', (qr_img.width, new_height), 'white')
            
            # Paste QR code
            new_img.paste(qr_img, (0, 0))
            
            # Add text
            draw = ImageDraw.Draw(new_img)
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (qr_img.width - text_width) // 2
            text_y = qr_img.height + 10
            
            # Draw text
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            return new_img
        except Exception as e:
            print(f"Error adding text to QR: {e}")
            return qr_img
    
    @staticmethod
    def generate_qr_svg(data: str) -> str:
        """Generate QR code as SVG string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(image_factory=SvgPathImage)
        
        # Convert to string
        byte_io = io.BytesIO()
        img.save(byte_io)
        byte_io.seek(0)
        
        return byte_io.getvalue().decode('utf-8')
    
    @staticmethod
    def save_qr_files(url: str, base_path: str = 'app/static/qr'):
        """Save QR codes as PNG and SVG files"""
        # Ensure directory exists
        Path(base_path).mkdir(parents=True, exist_ok=True)
        
        # Generate and save PNG
        png_filename = QRService.generate_qr_png(url, "portal.png")
        png_path = os.path.join(base_path, png_filename)
        
        # Generate and save SVG
        svg_data = QRService.generate_qr_svg(url)
        svg_path = os.path.join(base_path, 'portal.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_data)
        
        return {
            'png': png_path,
            'svg': svg_path
        }
    
    @staticmethod
    def generate_social_media_qr_batch(platforms_data: dict, size: str = "medium") -> dict:
        """Generate QR codes for multiple social media platforms"""
        base_path = 'app/static/qr'
        Path(base_path).mkdir(parents=True, exist_ok=True)
        
        size_mapping = {
            'small': 200,
            'medium': 400,
            'large': 600
        }
        pixel_size = size_mapping.get(size, 400)
        
        results = {}
        
        for platform, data in platforms_data.items():
            if not data.get('enabled', False) or not data.get('qr_enabled', False):
                continue
                
            url = data.get('url', '')
            if not url:
                continue
            
            # Get platform-specific styling
            color = QRService._get_platform_color(platform)
            display_name = QRService._get_platform_display_name(platform)
            
            # Generate QR code
            filename = f"social_{platform}_{size}.png"
            try:
                generated_file = QRService.generate_qr_png(
                    url, 
                    filename,
                    size=pixel_size,
                    logo_text=display_name,
                    style="thai",
                    color=color
                )
                results[platform] = {
                    'filename': generated_file,
                    'url': url,
                    'display_name': display_name,
                    'color': color
                }
            except Exception as e:
                print(f"Error generating QR for {platform}: {e}")
                
        return results
    
    @staticmethod
    def _get_platform_color(platform: str) -> str:
        """Get brand color for platform"""
        colors = {
            'line': '#00B900',
            'facebook': '#1877F2',
            'instagram': '#E4405F',
            'tiktok': '#000000',
            'whatsapp': '#25D366',
            'youtube': '#FF0000',
            'google_business': '#4285F4'
        }
        return colors.get(platform, '#000000')
    
    @staticmethod
    def _get_platform_display_name(platform: str) -> str:
        """Get display name for platform"""
        names = {
            'line': 'LINE',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'tiktok': 'TikTok',
            'whatsapp': 'WhatsApp',
            'youtube': 'YouTube',
            'google_business': 'Google'
        }
        return names.get(platform, platform.title())