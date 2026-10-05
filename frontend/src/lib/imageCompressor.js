/**
 * imageCompressor.js — Fast client-side image downscaling for HealthifyMe
 *
 * Scales the long-edge dimension down (e.g. 1400px for skin, 1024px for food)
 * to eliminate 80-95% of upload payload overhead while preserving clear visual
 * texture details.
 */

export async function compressImageFile(file, options = {}) {
  const {
    maxDimension = 1200,
    quality = 0.82,
    mimeType = "image/jpeg"
  } = options;

  if (!file || !file.type.startsWith("image/")) {
    return null;
  }

  // Fallback promise for environments without Canvas / Image
  const fallbackRead = () =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  if (typeof window === "undefined" || !window.createImageBitmap && !window.Image) {
    return fallbackRead();
  }

  return new Promise((resolve) => {
    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);

      let width = img.naturalWidth || img.width;
      let height = img.naturalHeight || img.height;

      if (!width || !height) {
        fallbackRead().then(resolve);
        return;
      }

      // Calculate downscaled dimensions preserving aspect ratio
      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = Math.round((height * maxDimension) / width);
          width = maxDimension;
        } else {
          width = Math.round((width * maxDimension) / height);
          height = maxDimension;
        }
      }

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext("2d");
      if (!ctx) {
        fallbackRead().then(resolve);
        return;
      }

      // Smooth resizing quality
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, 0, 0, width, height);

      try {
        const compressedBase64 = canvas.toDataURL(mimeType, quality);
        resolve(compressedBase64);
      } catch {
        fallbackRead().then(resolve);
      }
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      fallbackRead().then(resolve);
    };

    img.src = objectUrl;
  });
}
