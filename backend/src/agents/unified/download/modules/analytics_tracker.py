"""
Analytics Tracker Module
Tracks download analytics and usage patterns
"""

import asyncio
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class DownloadEvent:
    event_id: str
    token: str
    client_ip: str
    user_agent: str
    file_path: str
    file_size: int
    download_started: datetime
    download_completed: Optional[datetime]
    bytes_transferred: int
    success: bool
    error_message: str
    duration_seconds: float
    referrer: str
    country: str
    device_type: str


@dataclass
class AnalyticsReport:
    period: str
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    total_bytes: int
    average_file_size: float
    average_download_time: float
    popular_formats: Dict[str, int]
    geographic_distribution: Dict[str, int]
    device_breakdown: Dict[str, int]
    peak_hours: List[int]
    error_analysis: Dict[str, int]


class AnalyticsTracker:
    """Advanced analytics tracking for downloads"""

    def __init__(self):
        self.version = "1.0.0"

        self.analytics_config = {
            "enable_tracking": True,
            "track_ip_addresses": False,  # Privacy setting
            "data_retention_days": 90,
            "batch_size": 100,
            "export_formats": ["json", "csv"],
            "anonymize_data": True,
        }

        self.download_events = []
        self.aggregated_stats = defaultdict(int)

        # Initialize analytics storage
        self.analytics_dir = "/tmp/analytics"
        os.makedirs(self.analytics_dir, exist_ok=True)

    async def track_download_start(
        self, token: str, client_info: Dict[str, Any], file_info: Dict[str, Any]
    ) -> str:
        """Track start of download"""

        if not self.analytics_config["enable_tracking"]:
            return ""

        event_id = self._generate_event_id()

        # Extract and clean client information
        client_ip = client_info.get("ip", "unknown")
        if self.analytics_config["anonymize_data"]:
            client_ip = self._anonymize_ip(client_ip)

        user_agent = client_info.get("user_agent", "")
        referrer = client_info.get("referrer", "")

        # Detect device type and location
        device_type = self._detect_device_type(user_agent)
        country = self._detect_country(client_info.get("ip", ""))

        event = DownloadEvent(
            event_id=event_id,
            token=token[:8] + "...",  # Partial token for privacy
            client_ip=client_ip if not self.analytics_config["track_ip_addresses"] else "hidden",
            user_agent=self._sanitize_user_agent(user_agent),
            file_path=file_info.get("path", ""),
            file_size=file_info.get("size", 0),
            download_started=datetime.now(),
            download_completed=None,
            bytes_transferred=0,
            success=False,
            error_message="",
            duration_seconds=0.0,
            referrer=referrer,
            country=country,
            device_type=device_type,
        )

        self.download_events.append(event)

        # Update real-time stats
        self.aggregated_stats["total_started"] += 1
        self.aggregated_stats[f"device_{device_type}"] += 1
        self.aggregated_stats[f"country_{country}"] += 1

        return event_id

    async def track_download_progress(self, event_id: str, bytes_transferred: int) -> None:
        """Track download progress"""

        if not self.analytics_config["enable_tracking"]:
            return

        event = self._find_event_by_id(event_id)
        if event:
            event.bytes_transferred = bytes_transferred

    async def track_download_complete(
        self, event_id: str, success: bool, error_message: str = ""
    ) -> None:
        """Track completion of download"""

        if not self.analytics_config["enable_tracking"]:
            return

        event = self._find_event_by_id(event_id)
        if event:
            event.download_completed = datetime.now()
            event.success = success
            event.error_message = error_message

            if event.download_started:
                duration = event.download_completed - event.download_started
                event.duration_seconds = duration.total_seconds()

            # Update aggregated stats
            if success:
                self.aggregated_stats["total_completed"] += 1
                self.aggregated_stats["total_bytes"] += event.bytes_transferred
            else:
                self.aggregated_stats["total_failed"] += 1
                self.aggregated_stats[f"error_{error_message}"] += 1

            # Track file format
            file_ext = os.path.splitext(event.file_path)[1]
            self.aggregated_stats[f"format_{file_ext}"] += 1

    async def generate_analytics_report(self, period: str = "last_24h") -> AnalyticsReport:
        """Generate comprehensive analytics report"""

        # Define time period
        end_time = datetime.now()

        if period == "last_24h":
            start_time = end_time - timedelta(hours=24)
        elif period == "last_7d":
            start_time = end_time - timedelta(days=7)
        elif period == "last_30d":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=24)

        # Filter events for period
        period_events = [
            event for event in self.download_events if event.download_started >= start_time
        ]

        # Calculate basic metrics
        total_downloads = len(period_events)
        successful_downloads = len([e for e in period_events if e.success])
        failed_downloads = total_downloads - successful_downloads

        total_bytes = sum(e.bytes_transferred for e in period_events if e.success)

        average_file_size = (
            sum(e.file_size for e in period_events) / total_downloads if total_downloads > 0 else 0
        )

        successful_events = [e for e in period_events if e.success]
        average_download_time = (
            sum(e.duration_seconds for e in successful_events) / len(successful_events)
            if successful_events
            else 0
        )

        # Analyze popular formats
        popular_formats = defaultdict(int)
        for event in period_events:
            file_ext = os.path.splitext(event.file_path)[1] or "unknown"
            popular_formats[file_ext] += 1

        # Geographic distribution
        geographic_distribution = defaultdict(int)
        for event in period_events:
            geographic_distribution[event.country] += 1

        # Device breakdown
        device_breakdown = defaultdict(int)
        for event in period_events:
            device_breakdown[event.device_type] += 1

        # Peak hours analysis
        hour_distribution = defaultdict(int)
        for event in period_events:
            hour = event.download_started.hour
            hour_distribution[hour] += 1

        peak_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_hours = [hour for hour, _ in peak_hours]

        # Error analysis
        error_analysis = defaultdict(int)
        for event in period_events:
            if not event.success and event.error_message:
                error_analysis[event.error_message] += 1

        return AnalyticsReport(
            period=period,
            total_downloads=total_downloads,
            successful_downloads=successful_downloads,
            failed_downloads=failed_downloads,
            total_bytes=total_bytes,
            average_file_size=average_file_size,
            average_download_time=average_download_time,
            popular_formats=dict(popular_formats),
            geographic_distribution=dict(geographic_distribution),
            device_breakdown=dict(device_breakdown),
            peak_hours=peak_hours,
            error_analysis=dict(error_analysis),
        )

    async def export_analytics(self, format: str = "json", period: str = "last_24h") -> str:
        """Export analytics data"""

        report = await self.generate_analytics_report(period)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_{period}_{timestamp}.{format}"
        filepath = os.path.join(self.analytics_dir, filename)

        if format == "json":
            with open(filepath, "w") as f:
                json.dump(asdict(report), f, indent=2, default=str)

        elif format == "csv":
            import csv

            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)

                # Write summary
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Period", report.period])
                writer.writerow(["Total Downloads", report.total_downloads])
                writer.writerow(["Successful Downloads", report.successful_downloads])
                writer.writerow(["Failed Downloads", report.failed_downloads])
                writer.writerow(["Total Bytes", report.total_bytes])
                writer.writerow(["Average File Size", report.average_file_size])
                writer.writerow(["Average Download Time", report.average_download_time])

                # Write popular formats
                writer.writerow([])
                writer.writerow(["Popular Formats"])
                for format_name, count in report.popular_formats.items():
                    writer.writerow([format_name, count])

        return filepath

    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time download statistics"""

        current_hour = datetime.now().hour
        last_hour_events = [
            e for e in self.download_events if e.download_started.hour == current_hour
        ]

        return {
            "current_downloads": len(
                [e for e in self.download_events if e.download_completed is None]
            ),
            "downloads_this_hour": len(last_hour_events),
            "success_rate_this_hour": (
                len([e for e in last_hour_events if e.success]) / len(last_hour_events)
                if last_hour_events
                else 0
            ),
            "total_events_tracked": len(self.download_events),
            "total_bytes_served": self.aggregated_stats["total_bytes"],
            "most_popular_format": self._get_most_popular_format(),
            "active_countries": len(set(e.country for e in self.download_events)),
            "last_updated": datetime.now().isoformat(),
        }

    async def cleanup_old_data(self) -> int:
        """Clean up old analytics data"""

        retention_days = self.analytics_config["data_retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        original_count = len(self.download_events)

        self.download_events = [
            event for event in self.download_events if event.download_started > cutoff_date
        ]

        cleaned_count = original_count - len(self.download_events)

        # Clean up aggregated stats (simplified)
        # In production, implement proper aggregated data cleanup

        return cleaned_count

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""

        timestamp = datetime.now().isoformat()
        random_data = os.urandom(8).hex()
        event_string = f"{timestamp}_{random_data}"

        return hashlib.md5(event_string.encode()).hexdigest()[:16]

    def _find_event_by_id(self, event_id: str) -> Optional[DownloadEvent]:
        """Find download event by ID"""

        for event in self.download_events:
            if event.event_id == event_id:
                return event
        return None

    def _anonymize_ip(self, ip: str) -> str:
        """Anonymize IP address for privacy"""

        if not ip or ip == "unknown":
            return "unknown"

        # Simple IP anonymization - zero out last octet
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"

        # For IPv6 or invalid IPs, return hash
        return hashlib.md5(ip.encode()).hexdigest()[:8]

    def _sanitize_user_agent(self, user_agent: str) -> str:
        """Sanitize user agent string"""

        if len(user_agent) > 200:
            user_agent = user_agent[:200] + "..."

        # Remove potentially sensitive information
        import re

        user_agent = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]", user_agent)
        user_agent = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL]",
            user_agent,
        )

        return user_agent

    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent"""

        ua_lower = user_agent.lower()

        if any(mobile in ua_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
            return "mobile"
        elif any(tablet in ua_lower for tablet in ["tablet", "ipad"]):
            return "tablet"
        elif any(bot in ua_lower for bot in ["bot", "crawler", "spider"]):
            return "bot"
        else:
            return "desktop"

    def _detect_country(self, ip: str) -> str:
        """Detect country from IP address (simplified)"""

        # In production, use a proper GeoIP service
        # For now, return simplified detection

        if not ip or ip == "unknown":
            return "unknown"

        # Simple localhost/private IP detection
        if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
            return "local"

        # For demo purposes, assign based on IP pattern
        # In production, integrate with MaxMind GeoIP or similar
        ip_hash = hashlib.md5(ip.encode()).hexdigest()
        country_codes = ["US", "UK", "DE", "FR", "JP", "CA", "AU", "IN", "BR", "CN"]
        return country_codes[int(ip_hash[0], 16) % len(country_codes)]

    def _get_most_popular_format(self) -> str:
        """Get most popular file format"""

        format_counts = defaultdict(int)
        for event in self.download_events:
            file_ext = os.path.splitext(event.file_path)[1] or "unknown"
            format_counts[file_ext] += 1

        if not format_counts:
            return "none"

        return max(format_counts.items(), key=lambda x: x[1])[0]

    async def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard"""

        report_24h = await self.generate_analytics_report("last_24h")
        report_7d = await self.generate_analytics_report("last_7d")
        real_time = await self.get_real_time_stats()

        return {
            "real_time": real_time,
            "last_24_hours": asdict(report_24h),
            "last_7_days": asdict(report_7d),
            "trends": {
                "downloads_growth": self._calculate_growth_rate(),
                "success_rate_trend": self._calculate_success_rate_trend(),
                "popular_formats_trend": self._get_format_trends(),
            },
        }

    def _calculate_growth_rate(self) -> float:
        """Calculate download growth rate"""

        now = datetime.now()
        yesterday = now - timedelta(days=1)
        day_before = now - timedelta(days=2)

        yesterday_count = len(
            [e for e in self.download_events if day_before <= e.download_started < yesterday]
        )

        today_count = len([e for e in self.download_events if e.download_started >= yesterday])

        if yesterday_count == 0:
            return 0.0

        return ((today_count - yesterday_count) / yesterday_count) * 100

    def _calculate_success_rate_trend(self) -> List[float]:
        """Calculate success rate trend over last 7 days"""

        trends = []

        for i in range(7):
            day_start = datetime.now() - timedelta(days=i + 1)
            day_end = day_start + timedelta(days=1)

            day_events = [
                e for e in self.download_events if day_start <= e.download_started < day_end
            ]

            if day_events:
                success_rate = len([e for e in day_events if e.success]) / len(day_events)
                trends.append(success_rate * 100)
            else:
                trends.append(0.0)

        return list(reversed(trends))  # Return chronologically

    def _get_format_trends(self) -> Dict[str, List[int]]:
        """Get format popularity trends over last 7 days"""

        format_trends = defaultdict(lambda: [0] * 7)

        for i in range(7):
            day_start = datetime.now() - timedelta(days=i + 1)
            day_end = day_start + timedelta(days=1)

            day_events = [
                e for e in self.download_events if day_start <= e.download_started < day_end
            ]

            day_formats = defaultdict(int)
            for event in day_events:
                file_ext = os.path.splitext(event.file_path)[1] or "unknown"
                day_formats[file_ext] += 1

            for format_name, count in day_formats.items():
                format_trends[format_name][6 - i] = count

        return dict(format_trends)
