<script setup>
/**
 * 全局页脚组件。
 *
 * 用于呈现平台品牌信息、关键导航与联系信息，作为前端信息架构的
 * 收束节点，强化旅游信息系统的权威与可信度。
 */
</script>

<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="brand-block">
        <img
          class="footer-logo"
          src="/logo-mark-v2.png"
          alt="醉美遵义 · 山河红韵"
          width="52"
          height="52"
          loading="lazy"
          decoding="async"
        />
        <div class="brand-text">
          <h3>醉美遵义 · 山河红韵</h3>
          <p>Enchanting Zunyi · Red Heritage, Timeless Landscapes</p>
        </div>
      </div>

      <div class="footer-links">
        <!-- <router-link to="/overview">红城印象</router-link>
        <router-link to="/highlights">红城胜景</router-link>
        <router-link to="/taste">寻味遵义</router-link> -->
      </div>

      <div class="meta-block">
        <p>联系地址：贵州省安顺市西秀区学院路25号</p>
        <p>联系电话：182-7548-1854</p>
      </div>
    </div>

    <div class="copyright">
      © 2026 醉美遵义 · 山河红韵 | 基于 Flask + Vue
      的遵义旅游信息展示与文化传播系统
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  margin-top: auto;
  color: #f7f0e5;
  background:
    radial-gradient(
      circle at 15% 20%,
      rgba(181, 138, 75, 0.2),
      transparent 35%
    ),
    radial-gradient(
      circle at 85% 80%,
      rgba(255, 255, 255, 0.1),
      transparent 30%
    ),
    linear-gradient(135deg, #202724 0%, #2d312e 48%, #5d121b 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.footer-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 32px 20px 22px;
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 24px;
  align-items: center;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.footer-logo {
  width: 52px;
  height: 52px;
  padding: 4px;
  border: 1px solid rgba(238, 227, 210, 0.24);
  border-radius: 15px;
  background: rgba(252, 250, 245, 0.92);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.brand-text h3 {
  margin: 0;
  font-size: 18px;
  line-height: 1.1;
}

.brand-text p {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(247, 240, 229, 0.78);
}

.footer-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.footer-links a:hover {
  background: rgba(255, 255, 255, 0.14);
}

.meta-block {
  text-align: right;
  font-size: 13px;
  color: rgba(247, 240, 229, 0.78);
}

.meta-block p {
  margin: 4px 0;
}

.copyright {
  border-top: 1px solid rgba(255, 255, 255, 0.18);
  text-align: center;
  padding: 12px 16px 14px;
  font-size: 12px;
  color: rgba(247, 240, 229, 0.68);
}

@media (max-width: 960px) {
  .footer-inner {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 16px;
  }

  .brand-block {
    justify-content: center;
  }

  .meta-block {
    text-align: center;
  }
}
</style>
