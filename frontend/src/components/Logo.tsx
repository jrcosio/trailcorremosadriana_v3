// Feature 012 · US3, US4 y US8 (decisiones P7, P8 y P11): logotipo oficial del propietario.
// La cabecera usa el original. El pie y el panel tienen fondo oscuro y usan la versión en negativo.
// `sizes` refleja el ancho mostrado en cada sitio (ajustes.css A-005, A-006 y A-008).
const LOGOS = {
  cabecera: { base: '/reused/logos/logo_cabecera-', sizes: '(max-width:359px) 153px, (max-width:700px) 181px, (max-width:1000px) 212px, (max-width:1200px) 218px, 249px' },
  pie: { base: '/reused/logos/logo_pie-', sizes: '233px' },
  panel: { base: '/reused/logos/logo_pie-', sizes: '180px' },
  acceso: { base: '/reused/logos/logo_pie-', sizes: '261px' },
};

/** Imagen del logotipo con sus variantes de 480 y 720 px. La del pie se carga en diferido. */
export function LogoImg({ en }: { en: keyof typeof LOGOS }) {
  const { base, sizes } = LOGOS[en];
  return <img src={base + '480.webp'} srcSet={`${base}480.webp 480w, ${base}720.webp 720w`} sizes={sizes} width={480} height={154} loading={en === 'pie' ? 'lazy' : undefined} alt="Trail Peñasagra · Corremos por Adriana" />;
}
