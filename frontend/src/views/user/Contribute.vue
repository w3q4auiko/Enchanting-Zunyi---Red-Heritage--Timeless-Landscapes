<template>
  <div class="contribute-page">
    
    <div class="bg-decoration"></div>

    <main class="form-container animate-fade-in">
      
      <header class="form-header">
        <div class="brand-badge">Community Driven</div>
        <h1>分享您的遵义印记</h1>
        <p class="sub-title">
          每一份真实的记录，都是对这片红土地最深情的告白。您的贡献将帮助更多探索者发现隐匿的黔北风情。
        </p>
      </header>

      
      <div class="form-card">
        <div class="form-grid">
          
          <section class="form-section">
            <div class="section-title">
              <span class="number">01</span>
              <h3>基础概况</h3>
            </div>

            <div class="form-item">
              <label>投稿维度</label>
              <div class="type-segment-control">
                <button
                  v-for="type in typeOptions"
                  :key="type.value"
                  :class="{ active: form.type === type.value }"
                  type="button"
                  @click="form.type = type.value"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>

            <div class="form-item">
              <label>实体名称 <span class="req">*</span></label>
              <input
                v-model.trim="form.title"
                placeholder="赋予一个具有吸引力的标题"
                type="text"
                class="v-input"
              />
            </div>

            
            <transition name="slide-fade">
              <div v-if="form.type !== 'route'" class="form-item">
                <label>寻址位置 <span class="req">*</span></label>
                <div class="input-with-icon">
                  <span class="prefix-icon">📍</span>
                  <input
                    v-model.trim="form.address"
                    placeholder="省/市/区/详细街道"
                    type="text"
                  />
                </div>
              </div>
            </transition>
          </section>

          
          <section class="form-section">
            <div class="section-title">
              <span class="number">02</span>
              <h3>详细叙事</h3>
            </div>

            
            <div class="dynamic-params">
              <transition mode="out-in" name="slide-up">
                <div
                  v-if="form.type === 'food'"
                  :key="'food'"
                  class="form-item"
                >
                  <label>消费基准 (人均)</label>
                  <input
                    v-model.trim="form.price"
                    placeholder="例如：¥25-40"
                    type="text"
                  />
                </div>
                <div
                  v-else-if="form.type === 'route'"
                  :key="'route'"
                  class="form-item"
                >
                  <label>运动学参数</label>
                  <input
                    v-model.trim="form.extra"
                    placeholder="全长、海拔、建议时长"
                    type="text"
                  />
                </div>
              </transition>
            </div>

            <div class="form-item">
              <label>视觉素材</label>
              <ImageUploader
                v-model="form.image"
                scope="submission"
                hint="从电脑或手机选择 JPG、PNG、WebP 图片，单张不超过 5MB"
              />
            </div>

            <div class="form-item">
              <label>推荐理由与人文叙事 <span class="req">*</span></label>
              <textarea
                v-model.trim="form.desc"
                placeholder="写下这里的独特之处，或是那次难忘的邂逅..."
                rows="5"
              ></textarea>
            </div>
          </section>
        </div>

        
        <footer class="form-footer">
          <button :disabled="loading" class="submit-btn" @click="handleSubmit">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? "正在同步至云端..." : "确认发布投稿" }}
          </button>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup>
/**
 * @file Contribute.vue
 * @description 用户投稿页，承载“共创内容”业务入口。
 * 设计意图：通过统一表单采集游客视角的景点、餐饮与路线线索。
 * 业务意义：投稿进入审核管线，补充旅游信息系统的长尾内容覆盖。
 */
import { reactive, ref } from "vue";
import request from "@/utils/request";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ensureSession } from "@/api/auth";
import ImageUploader from "@/components/ImageUploader.vue";

const router = useRouter();
const loading = ref(false);


const typeOptions = [
  { label: "自然人文", value: "scenery" },
  { label: "黔北食韵", value: "food" },
  { label: "户外路线", value: "route" },
];


const form = reactive({
  type: "scenery",
  title: "",
  address: "",
  price: "",
  extra: "",
  image: "",
  desc: "",
});


/**
 * 校验表单并提交到投稿审核管线。
 * @returns {Promise<void>} 提交完成后刷新状态或跳转。
 */
const handleSubmit = async () => {
  if (!form.title) return ElMessage.warning("请为您的投稿定义一个标题");
  if (form.type !== "route" && !form.address)
    return ElMessage.warning("请录入实体的物理寻址位置");
  if (!form.desc || form.desc.length < 10)
    return ElMessage.warning("描述内容过短，请补充更多细节");

  if (!(await ensureSession())) {
    ElMessage.error("未检测到有效鉴权凭证，请登录后操作");
    router.push("/login");
    return;
  }

  loading.value = true;
  try {
    const res = await request.post("/submission/add", form);

    if (res.code === 200 || res.code === 201) {
      ElMessage({
        message: "投稿已成功进入审核管线！预计 48 小时内完成核验。",
        type: "success",
        duration: 3000,
      });
      setTimeout(() => router.push("/"), 2000);
    } else {
      ElMessage.error(res.error || "服务端持久化异常，请检查输入格式");
    }
  } catch (e) {
    console.error("Critical: Submission Transaction Aborted.", e);
    ElMessage.error("底层网络链路异常或服务暂不可用");
  } finally {
    loading.value = false;
  }
};


</script>

<style scoped>


.contribute-page {
  position: relative;
  min-height: 100vh;
  padding: 4rem 1.5rem;
  background-color: #f1eae0;
  overflow: hidden;
  display: flex;
  justify-content: center;
}


.bg-decoration {
  position: absolute;
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(
    circle,
    rgba(139, 0, 0, 0.05) 0%,
    transparent 70%
  );
  z-index: 0;
}

.form-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 960px;
}



.form-header {
  text-align: center;
  margin-bottom: 3rem;
}

.brand-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: #f2d8da;
  color: #a61f2d;
  font-size: 0.75rem;
  font-weight: 800;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 900;
  color: #29312e;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.sub-title {
  color: #746f67;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}



.form-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; 
  gap: 3rem;
}

@media (max-width: 860px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  .form-card {
    padding: 1.5rem;
  }
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.section-title .number {
  font-size: 0.875rem;
  font-weight: 800;
  color: #8d1b28;
  background: #f8eeee;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.section-title h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #29312e;
}



.form-item label {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: #5f615d;
  margin-bottom: 0.6rem;
}


.type-segment-control {
  display: flex;
  background: #f1eae0;
  padding: 4px;
  border-radius: 12px;
  gap: 4px;
}

.type-segment-control button {
  flex: 1;
  border: none;
  padding: 0.7rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #746f67;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.type-segment-control button.active {
  background: white;
  color: #8d1b28;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}


input,
textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #f1eae0;
  border-radius: 12px;
  font-size: 0.95rem;
  color: #29312e;
  transition: all 0.2s;
  background: #fcfaf5;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #8d1b28;
  background: white;
  box-shadow: 0 0 0 4px rgba(139, 0, 0, 0.05);
}


.input-with-icon {
  position: relative;
}
.prefix-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
}
.input-with-icon input {
  padding-left: 2.8rem;
}


.form-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #f1eae0;
}

.terms-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.submit-btn {
  width: 100%;
  padding: 1.25rem;
  background: linear-gradient(135deg, #8d1b28 0%, #a61f2d 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px -10px rgba(139, 0, 0, 0.4);
}

.submit-btn:disabled {
  filter: grayscale(0.8);
  opacity: 0.6;
  cursor: not-allowed;
}



.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.spinner {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

