/**
 * 前端静态资源压缩脚本。
 *
 * 该脚本在构建阶段统一处理图片压缩与 WebP 生成，作为旅游信息系统
 * 视觉资产治理的一部分，用于降低首屏负载与提升多终端访问效率。
 */
import fs from "fs/promises";
import path from "path";
import sharp from "sharp";

const rootDir = process.cwd();
const targetDir = path.join(rootDir, "public", "img");
const args = new Set(process.argv.slice(2));

const overwriteOriginal = args.has("--in-place");
const quality = Number(process.env.IMAGE_QUALITY || 75);
const webpQuality = Number(process.env.WEBP_QUALITY || quality);
const minSavings = Number(process.env.MIN_SAVINGS || 0.05);

const supportedExts = new Set([".jpg", ".jpeg", ".png"]);

/**
 * 判断指定路径是否存在。
 *
 * @param {string} filePath - 目标路径。
 * @returns {Promise<boolean>} 是否存在。
 */
const fileExists = async (filePath) => {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
};

/**
 * 递归枚举目录下的文件列表。
 *
 * @param {string} dir - 起始目录。
 * @returns {Promise<string[]>} 文件路径列表。
 */
const walk = async (dir) => {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(fullPath)));
    } else {
      files.push(fullPath);
    }
  }

  return files;
};

/**
 * 依据原始格式执行重编码。
 *
 * @param {string} inputPath - 原始图片路径。
 * @param {string} ext - 文件扩展名（含点号）。
 * @returns {import("sharp").Sharp} Sharp 实例。
 */
const encodeOriginal = async (inputPath, ext) => {
  if (ext === ".png") {
    return sharp(inputPath).png({
      compressionLevel: 9,
      palette: true,
      quality,
    });
  }
  return sharp(inputPath).jpeg({
    quality,
    mozjpeg: true,
  });
};

/**
 * 执行批量图片优化流程。
 *
 * 该流程确保旅游系统前端图像在不显著损失观感的前提下压缩体积，
 * 同时生成 WebP 版本以适配现代浏览器的高效传输。
 *
 * @returns {Promise<void>}
 */
const optimizeImages = async () => {
  const stats = {
    scanned: 0,
    webpCreated: 0,
    webpSkipped: 0,
    optimized: 0,
    optimizedSkipped: 0,
    errors: 0,
  };

  if (!(await fileExists(targetDir))) {
    console.error(`[image-opt] Missing directory: ${targetDir}`);
    process.exitCode = 1;
    return;
  }

  const files = await walk(targetDir);

  for (const file of files) {
    const ext = path.extname(file).toLowerCase();
    if (!supportedExts.has(ext)) continue;

    stats.scanned += 1;
    const webpPath = file.replace(/\.(jpe?g|png)$/i, ".webp");

    try {
      const srcStat = await fs.stat(file);
      const shouldCreateWebp =
        !(await fileExists(webpPath)) ||
        (await fs.stat(webpPath)).mtimeMs < srcStat.mtimeMs;

      if (shouldCreateWebp) {
        await sharp(file).webp({ quality: webpQuality }).toFile(webpPath);
        stats.webpCreated += 1;
      } else {
        stats.webpSkipped += 1;
      }

      if (overwriteOriginal) {
        const tmpPath = `${file}.tmp`;
        await encodeOriginal(file, ext).toFile(tmpPath);
        const tmpStat = await fs.stat(tmpPath);
        if (tmpStat.size < srcStat.size * (1 - minSavings)) {
          await fs.rename(tmpPath, file);
          stats.optimized += 1;
        } else {
          await fs.unlink(tmpPath);
          stats.optimizedSkipped += 1;
        }
      }
    } catch (error) {
      stats.errors += 1;
      console.error(`[image-opt] Failed: ${file}`, error);
    }
  }

  console.log(
    `[image-opt] Scanned: ${stats.scanned}, WebP: ${stats.webpCreated} created, ${stats.webpSkipped} skipped, ` +
      `In-place optimized: ${stats.optimized}, skipped: ${stats.optimizedSkipped}, errors: ${stats.errors}`
  );
};

optimizeImages();
