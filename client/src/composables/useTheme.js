import { ref, computed, watch } from "vue";

const getInitialTheme = () => {
  const stored = localStorage.getItem("theme");
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    return "dark";
  }

  return "light";
};

const theme = ref(getInitialTheme());

const applyTheme = (value) => {
  document.documentElement.setAttribute("data-theme", value);
  localStorage.setItem("theme", value);
};

applyTheme(theme.value);

watch(theme, (value) => {
  applyTheme(value);
});

export function useTheme() {
  const isDark = computed(() => theme.value === "dark");

  const toggleTheme = () => {
    theme.value = theme.value === "dark" ? "light" : "dark";
  };

  return {
    theme,
    isDark,
    toggleTheme,
  };
}
