# Bit depth and continuous height resolution

Keep the reusable source master and target build heightmap as 16-bit grayscale PNG by default. Internal processing should use float or 16-bit precision.

16-bit design precision does not mean the printer physically realizes 65,536 Z levels. It prevents premature tonal loss during resize, gamma, wrap, and displacement.

Do not threshold, palette-reduce, posterize, or intentionally quantize a portrait, animal, object, texture, or tonal logo unless the user requests a stepped style.

If relief is visually weak, change physical depth, placed size, local contrast/gamma, print orientation, or emboss/engrave direction. Do not destroy grayscale to make the model appear stronger.
