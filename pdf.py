import os
import time
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import meraki
from fpdf import FPDF
from fpdf.enums import XPos, YPos

load_dotenv("config.env")
API_KEY = os.getenv("MERAKI_API_KEY")
ORG_ID = os.getenv("MERAKI_ORG_ID")

dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 70, 130)
        self.cell(0, 10, "Meraki Wireless AP Uptime Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "", 10)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cell(0, 10, f"Generated: {timestamp}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

    def section_title(self, title):
        self.set_fill_color(230, 240, 255)
        self.set_text_color(0)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    def analytics_summary(self, total_nets, total_aps, avg_uptime, top3, ap_down_count):
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, f"Total Networks Monitored: {total_nets}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 8, f"Total Access Points: {total_aps}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 8, f"Average Uptime (24h): {avg_uptime}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 8, f"APs Down in Last 24h: {ap_down_count}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Top 3 Networks with Lowest Uptime (24h):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 10)
        for net in top3:
            self.cell(0, 8, f"- {net['network']} ({net['avg_uptime']}%)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def table(self, headers, rows, col_widths):
        self.set_font("Helvetica", "B", 10)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 10, h, border=1, align='C')
        self.ln()
        self.set_font("Helvetica", "", 9)

        for row in rows:
            x_start = self.get_x()
            y_start = self.get_y()
            line_heights = []

            for i, text in enumerate(row):
                lines = self.multi_cell(col_widths[i], 5, str(text), border=0, align='L', dry_run=True, output="LINES")
                line_heights.append(len(lines))

            max_lines = max(line_heights)
            row_height = max_lines * 5

            for i, text in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 5, str(text), border=1, align='L')

            self.set_y(y_start + row_height)

def calculate_uptime_from_events(events, start_time, end_time):
    events = sorted(events, key=lambda x: x['occurredAt'])
    current_state = 'up'
    last_time = start_time
    uptime = timedelta()
    downtime = timedelta()

    for event in events:
        occurred = datetime.fromisoformat(event['occurredAt'].replace("Z", "+00:00"))
        duration = occurred - last_time
        if current_state == 'up':
            uptime += duration
        else:
            downtime += duration
        current_state = 'down' if event['eventType'] == 'ap_down' else 'up'
        last_time = occurred

    remaining = end_time - last_time
    if current_state == 'up':
        uptime += remaining
    else:
        downtime += remaining

    total = uptime + downtime
    return round(uptime.total_seconds() / total.total_seconds() * 100, 2) if total.total_seconds() > 0 else 0.0

def get_ap_event_logs(network_id, serial, timespan_sec):
    try:
        return dashboard.networks.getNetworkEvents(
            network_id,
            productType='wireless',
            includedEventTypes=['ap_up', 'ap_down'],
            deviceSerial=serial,
            perPage=1000,
            t0=(datetime.utcnow() - timedelta(seconds=timespan_sec)).isoformat() + "Z"
        ).get('events', [])
    except Exception as e:
        print(f"⚠️ Error for {serial}: {e}")
        return []

def generate_report():
    networks = dashboard.organizations.getOrganizationNetworks(ORG_ID)
    network_map = {n['id']: n['name'] for n in networks if 'wireless' in n.get('productTypes', [])}
    statuses = dashboard.organizations.getOrganizationDevicesStatuses(ORG_ID)
    aps = [d for d in statuses if d.get('model', '').startswith('MR')]

    ap_rows, summary_rows, ap_down_24h = [], [], []
    network_uptime = defaultdict(list)
    now = datetime.utcnow()

    for ap in aps:
        serial = ap['serial']
        net_id = ap.get('networkId')
        if not net_id:
            continue

        net_name = network_map.get(net_id, "Unknown")
        hostname = ap.get('name', 'Unnamed')
        status = ap.get('status', 'unknown')

        ev_24h = get_ap_event_logs(net_id, serial, 24 * 3600)
        ev_7d = get_ap_event_logs(net_id, serial, 7 * 24 * 3600)

        up_24h = calculate_uptime_from_events(ev_24h, now - timedelta(hours=24), now)
        up_7d = calculate_uptime_from_events(ev_7d, now - timedelta(days=7), now)

        print(f"[{hostname}] Status: {status} | 24h: {up_24h}% | 7d: {up_7d}%")

        ap_rows.append([net_name, hostname, status, f"{up_24h}%", f"{up_7d}%"])
        network_uptime[net_name].append(up_24h)

        if any(e['eventType'] == 'ap_down' for e in ev_24h):
            ap_down_24h.append([net_name, hostname, status, f"{up_24h}%", f"{up_7d}%"])

        time.sleep(0.2)

    for i, (net, uptimes) in enumerate(network_uptime.items(), 1):
        avg = round(sum(uptimes) / len(uptimes), 2)
        summary_rows.append([str(i), net, str(len(uptimes)), f"{avg}%"])

    return summary_rows, ap_rows, ap_down_24h

def generate_pdf(summary, ap_rows, ap_down):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"meraki_ap_uptime_report_{timestamp}.pdf"
    pdf = PDF()
    pdf.add_page()

    total_nets = len(summary)
    total_aps = sum(int(row[2]) for row in summary)
    avg_uptime = round(sum(float(row[3].replace('%','')) for row in summary) / total_nets, 2)
    top3 = sorted([{'network': row[1], 'avg_uptime': row[3]} for row in summary], key=lambda x: float(x['avg_uptime'].replace('%','')))[:3]

    pdf.section_title("Executive Summary")
    pdf.analytics_summary(total_nets, total_aps, avg_uptime, top3, len(ap_down))

    pdf.section_title("Network-wise Summary")
    pdf.table(["S.No", "Network Name", "Total AP", "Avg Uptime (24h)"], summary, [15, 80, 25, 50])

    pdf.section_title("AP-wise Uptime (24h & 7d)")
    pdf.table(["Network", "Hostname", "Status", "24h Uptime", "7d Uptime"], ap_rows, [45, 55, 20, 30, 30])

    if ap_down:
        pdf.section_title("APs Down in Last 24 Hours")
        pdf.table(["Network", "Hostname", "Status", "24h Uptime", "7d Uptime"], ap_down, [45, 55, 20, 30, 30])

    pdf.output(filename)
    print(f"\n✅ PDF generated: {filename}")

if __name__ == "__main__":
    if not API_KEY or not ORG_ID:
        print("❌ Please check your MERAKI_API_KEY or ORG_ID in config.env")
    else:
        summary, ap_rows, ap_down = generate_report()
        generate_pdf(summary, ap_rows, ap_down)
