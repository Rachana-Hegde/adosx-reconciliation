from rest_framework.response import Response
from rest_framework.views import APIView

from reconciliation.comparison import build_disagreements
from reconciliation.models import (
    SystemARecord,
    SystemBEntry,
)
from reconciliation.serializers import (
    DisagreementSerializer,
)


class DisagreementListView(APIView):

    def get(self, request):
        a_records = list(
            SystemARecord.objects.select_related(
                "location__organization"
            ).all()
        )

        b_entries = list(
            SystemBEntry.objects.select_related(
                "location__organization"
            ).all()
        )

        disagreements = build_disagreements(
            a_records,
            b_entries,
        )

        # -----------------------------------------------------
        # Filter by reason
        # -----------------------------------------------------

        reason = request.query_params.get("reason")

        if reason:
            disagreements = [
                item
                for item in disagreements
                if item["reason"] == reason
            ]

        # -----------------------------------------------------
        # Sort by value
        # -----------------------------------------------------

        sort = request.query_params.get("sort")

        if sort == "value":
            disagreements.sort(
                key=lambda item: self.sort_value(
                    item["system_a_value"]
                )
            )

        elif sort == "-value":
            disagreements.sort(
                key=lambda item: self.sort_value(
                    item["system_a_value"]
                ),
                reverse=True,
            )

        serializer = DisagreementSerializer(
            disagreements,
            many=True,
        )

        return Response(
            {
                "count": len(disagreements),
                "results": serializer.data,
            }
        )

    @staticmethod
    def sort_value(value):
        if isinstance(value, (int, float)):
            return value

        if value is None:
            return 0

        try:
            cleaned = str(value).replace(",", "").strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return 0