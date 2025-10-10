import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';

const languages: { code: string; label: string }[] = [
  { code: 'ro', label: 'RO' },
  { code: 'en', label: 'EN' }
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  return (
    <div className="flex items-center gap-1">
      {languages.map(({ code, label }) => (
        <Button
          key={code}
          variant={i18n.language === code ? 'default' : 'ghost'}
          size="sm"
          onClick={() => i18n.changeLanguage(code)}
        >
          {label}
        </Button>
      ))}
    </div>
  );
}

export default LanguageSwitcher;
