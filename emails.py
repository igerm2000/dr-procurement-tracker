"""Email HTML generation -- matches the mockup design approved earlier."""

def format_dt(dt):
    return dt.strftime("%d/%m %H:%M")


def instant_email(p):
    subject = f"Nuevo proceso: {p['matched_keyword']} — {p['referencia']}"
    html = f"""
    <div style="font-family: sans-serif; max-width: 520px;">
      <h2 style="font-size:16px;">{p['descripcion']}</h2>
      <p style="color:#555;">{p['institucion']}</p>
      <table style="font-size:13px; width:100%;">
        <tr><td style="color:#777;">Coincide con</td><td>{p['matched_keyword']}</td></tr>
        <tr><td style="color:#777;">Referencia</td><td>{p['referencia']}</td></tr>
        <tr><td style="color:#777;">Publicado</td><td>{format_dt(p['fecha_publicacion'])}</td></tr>
        <tr><td style="color:#777;">Cierre de ofertas</td><td>{format_dt(p['fecha_oferta'])}</td></tr>
        <tr><td style="color:#777;">Total estimado</td><td>{p['total_estimado']}</td></tr>
        <tr><td style="color:#777;">Estado</td><td>{p['estado']}</td></tr>
      </table>
      <p style="margin-top:16px;">
        <a href="{p.get('source_url', '')}">Ver en el portal</a>
      </p>
    </div>
    """.strip()
    return subject, html


def digest_email(pending_items, excluded_count):
    today_str = pending_items[0]["fecha_oferta"][:10] if pending_items else ""
    subject = f"Resumen del día — {len(pending_items)} proceso(s)"
    if not pending_items:
        body = "<p>No hubo procesos que coincidieran con tus palabras clave hoy.</p>"
    else:
        rows = "\n".join(
            f"""<div style="border-top:1px solid #eee; padding:10px 0;">
                  <b>{item['descripcion'][:80]}</b><br/>
                  <span style="color:#555; font-size:13px;">
                    {item['institucion']} · {item['referencia']}
                    · coincide: {item['matched_keyword']}
                    · cierra {item['fecha_oferta'][:16]}
                  </span>
                </div>"""
            for item in pending_items
        )
        body = f'<div style="font-family: sans-serif; max-width: 520px;">{rows}</div>'
    footer = f"<p style='color:#999; font-size:12px;'>{excluded_count} proceso(s) descartados por la ventana de cierre.</p>"
    return subject, body + footer
