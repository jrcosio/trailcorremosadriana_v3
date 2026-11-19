import { Heart, ExternalLink } from 'lucide-react';
import { solidarityRegistration } from '@/lib/registration';
import type { SiteData } from '@/lib/data';

export default function DorsalSolidario({ settings, variant = 'card' }: { settings: SiteData['settings']; variant?: 'banner' | 'card' }) {
  const action = solidarityRegistration(settings);
  return (
    <section className={'donation-callout donation-' + variant} aria-label="Dorsal solidario">
      <div className="donation-heart" aria-hidden="true"><Heart size={32} /></div>
      <div className="donation-copy">
        <span className="donation-eyebrow">CORREMOS POR ADRIANA</span>
        {variant === 'banner'
          ? <><h3>No hace falta correr<br />para dejar huella.</h3><p>Apoya a Adriana con tu <strong>dorsal solidario.</strong></p></>
          : <><h3>Dorsal solidario</h3><p>Sin distancia. Sin cronómetro.<br />Con todo el corazón.</p></>}
      </div>
      <div className="donation-action">
        {action.available
          ? <a className="button donation-button" href={action.href} target="_blank" rel="noopener noreferrer" aria-label="Pagar dorsal solidario en la web de inscripciones"><Heart size={18} />{action.label}<ExternalLink size={16} /></a>
          : <button className="button donation-button" disabled>{action.label}</button>}
        <p className="donation-note">{action.message}</p>
      </div>
    </section>
  );
}
