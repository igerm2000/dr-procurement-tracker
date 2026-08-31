"""Email HTML generation -- single daily digest, built from accumulated
pending items (already-formatted plain dicts, no datetime objects)."""


def digest_email(pending_items, excluded_count):
    if not pending_items:
        subject = "Resumen diario — no hay procesos nuevos"
        body = "<p>No se encontraron procesos nuevos que coincidan con tus palabras clave hoy.</p>"
    else:
        subject = f"Resumen diario — {len(pending_items)} proceso(s) nuevo(s)"
        rows = "\n".join(
            f"""<div style="border-top:1px solid #eee; padding:10px 0;">
                  <b>{item['descripcion'][:80]}</b><br/>
                  <span style="color:#555; font-size:13px;">
                    {item['institucion']} · {item['referencia']}<br/>
                    coincide: {item['matched_keyword']}
                    · cierra {item['fecha_oferta']}
                    · {item['total_estimado']}
                  </span>
                </div>"""
            for item in pending_items
        )
        body = f'<div style="font-family: sans-serif; max-width: 520px;">{rows}</div>'
    footer = (f"<p style='color:#999; font-size:12px; margin-top:14px;'>"
              f"{excluded_count} proceso(s) descartados hoy por la ventana de cierre "
              f"u otro filtro.</p>")
    return subject, body + footer
