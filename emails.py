"""Email HTML generation -- single daily digest, built from accumulated
pending items (already-formatted plain dicts, no datetime objects)."""


def digest_email(pending_items, excluded_count, fetch_ok=None, fetch_fail=0):
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
    if fetch_ok is not None:
        total = fetch_ok + fetch_fail
        if fetch_ok == 0:
            subject = "⚠ Resumen diario — el portal no respondió hoy"
            body = ("<p style='color:#b00;'><b>Atención:</b> ninguna de las "
                    f"{total} revisiones de hoy pudo leer el portal. "
                    "Este resumen NO significa que no hubo procesos.</p>") + body
        elif fetch_fail:
            body = ("<p style='color:#b60; font-size:13px;'>Aviso: "
                    f"{fetch_fail} de {total} revisiones de hoy no pudieron leer "
                    "el portal.</p>") + body
        footer += (f"<p style='color:#999; font-size:12px;'>Revisiones del portal hoy: "
                   f"{fetch_ok} correctas, {fetch_fail} fallidas.</p>")
    return subject, body + footer
