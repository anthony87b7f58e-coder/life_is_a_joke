import os
import logging
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

logger = logging.getLogger('bot.reporter')

class Reporter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.output_dir = cfg.get('report',{}).get('output_dir','./reports')
        os.makedirs(self.output_dir, exist_ok=True)

    async def start(self):
        # schedule weekly report job externally via cron or scheduler
        pass

    async def stop(self):
        pass

    def generate_weekly_report(self, metrics: dict, trades: list, filename=None):
        # generate both HTML and PDF summary
        filename = filename or f"weekly_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        path = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(path)
        styles = getSampleStyleSheet()
        story = [Paragraph('Weekly Trading Report', styles['Title']), Spacer(1,12)]
        for k,v in metrics.items():
            story.append(Paragraph(f"{k}: {v}", styles['Normal']))
        story.append(Spacer(1,12))
        doc.build(story)
        logger.info('Generated PDF report at %s', path)
        return path

    def sample_plot_equity(self, equity_curve, outpath):
        plt.figure(figsize=(8,4))
        plt.plot(equity_curve)
        plt.title('Equity Curve')
        plt.savefig(outpath)
        plt.close()
