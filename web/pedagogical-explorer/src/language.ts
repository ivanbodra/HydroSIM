import { useEffect, useState } from 'react';

export type HydroLocale = 'en' | 'pt-BR';
const STORAGE_KEY = 'hydrosim-locale';
const EVENT_NAME = 'hydrosim-language';

export function getHydroLocale(): HydroLocale {
  if (typeof window === 'undefined') return 'en';
  return localStorage.getItem(STORAGE_KEY) === 'pt-BR' ? 'pt-BR' : 'en';
}

export function setHydroLocale(locale: HydroLocale) {
  localStorage.setItem(STORAGE_KEY, locale);
  window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: locale }));
}

export function useHydroLocale() {
  const [locale, setLocale] = useState<HydroLocale>(getHydroLocale);
  useEffect(() => {
    const sync = (event: Event) => setLocale((event as CustomEvent<HydroLocale>).detail ?? getHydroLocale());
    window.addEventListener(EVENT_NAME, sync);
    window.addEventListener('storage', () => setLocale(getHydroLocale()));
    return () => window.removeEventListener(EVENT_NAME, sync);
  }, []);
  return [locale, setHydroLocale] as const;
}

export const languageTarget = (locale: HydroLocale) => locale === 'en' ? 'pt-BR' : 'en';
export const languageFlag = (locale: HydroLocale) => locale === 'en' ? '🇧🇷' : '🇺🇸';
