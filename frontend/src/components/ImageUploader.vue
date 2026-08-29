<script setup>
/**
 * 统一图片选择与上传组件。
 *
 * 从用户本地选择图片后立即上传，并将服务端返回的站内 URL
 * 回填到业务表单。仍保留手动 URL 输入，用于兼容已有 CDN 资源。
 */
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";

import request from "@/utils/request";
import { fixUrl } from "@/utils/common";

const props = defineProps({
  modelValue: { type: String, default: "" },
  scope: { type: String, default: "other" },
  compact: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  hint: { type: String, default: "支持 JPG、PNG、WebP，单张不超过 5MB" },
});

const emit = defineEmits(["update:modelValue", "uploaded"]);
const inputRef = ref(null);
const uploading = ref(false);
const progress = ref(0);
const previewFailed = ref(false);

const previewUrl = computed(() => fixUrl(props.modelValue));

const updateUrl = (value) => {
  previewFailed.value = false;
  emit("update:modelValue", value.trim());
};

const chooseFile = () => {
  if (!props.disabled && !uploading.value) inputRef.value?.click();
};

const uploadSelectedFile = async (event) => {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) return;

  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    ElMessage.warning("请选择 JPG、PNG 或 WebP 图片");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning("图片不能超过 5MB");
    return;
  }

  const body = new FormData();
  body.append("file", file);
  body.append("scope", props.scope);

  uploading.value = true;
  progress.value = 0;
  try {
    const result = await request.post("/media/images", body, {
      timeout: 30000,
      skipGlobalHandler: true,
      onUploadProgress: (uploadEvent) => {
        if (uploadEvent.total) {
          progress.value = Math.round(
            (uploadEvent.loaded / uploadEvent.total) * 100,
          );
        }
      },
    });
    emit("update:modelValue", result.url);
    emit("uploaded", result);
    previewFailed.value = false;
    ElMessage.success("图片上传成功");
  } catch (error) {
    ElMessage.error(error.response?.data?.error || "图片上传失败");
  } finally {
    uploading.value = false;
    progress.value = 0;
  }
};
</script>

<template>
  <div class="image-uploader" :class="{ 'is-compact': compact }">
    <div class="image-uploader-input-row">
      <input
        class="image-url-input"
        :disabled="disabled || uploading"
        :value="modelValue"
        type="text"
        placeholder="上传后自动生成图片地址，也可粘贴已有 URL"
        @input="updateUrl($event.target.value)"
      />
      <button
        class="image-choose-button"
        :disabled="disabled || uploading"
        type="button"
        @click="chooseFile"
      >
        {{ uploading ? `上传中 ${progress}%` : "选择图片" }}
      </button>
      <input
        ref="inputRef"
        class="sr-only-file"
        type="file"
        accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
        @change="uploadSelectedFile"
      />
    </div>

    <p class="image-upload-hint">{{ hint }}</p>

    <div class="image-preview">
      <img
        v-if="previewUrl && !previewFailed"
        :key="previewUrl"
        :src="previewUrl"
        alt="图片预览"
        loading="lazy"
        decoding="async"
        @error="previewFailed = true"
      />
      <span v-else>{{
        previewFailed ? "图片无法预览，请检查地址" : "尚未选择图片"
      }}</span>
    </div>
  </div>
</template>

<style scoped>
.image-uploader {
  width: 100%;
}

.image-uploader-input-row {
  display: flex;
  gap: 8px;
}

.image-url-input {
  min-width: 0;
  flex: 1;
  height: 40px;
  padding: 0 12px;
  color: #29312e;
  background: #fcfaf5;
  border: 1px solid #d8d1c7;
  border-radius: 8px;
  outline: none;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.image-url-input:focus {
  border-color: #a61f2d;
  box-shadow: 0 0 0 3px rgba(166, 31, 45, 0.1);
}

.image-choose-button {
  min-width: 124px;
  height: 40px;
  padding: 0 14px;
  color: #fff;
  font-weight: 700;
  background: #a61f2d;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.2s;
}

.image-choose-button:hover:not(:disabled) {
  background: #791722;
  transform: translateY(-1px);
}

.image-choose-button:disabled,
.image-url-input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.sr-only-file {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.image-upload-hint {
  margin: 7px 0 0;
  color: #8b857c;
  font-size: 11px;
  line-height: 1.5;
}

.image-preview {
  width: 100%;
  height: 142px;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #9b958d;
  font-size: 12px;
  background: #f4efe7;
  border: 1px dashed #d2c7b8;
  border-radius: 10px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.is-compact .image-preview {
  height: 108px;
}

@media (max-width: 640px) {
  .image-uploader-input-row {
    flex-direction: column;
  }

  .image-choose-button {
    width: 100%;
  }
}
</style>
