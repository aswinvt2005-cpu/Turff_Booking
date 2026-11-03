from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Turf.models import TurfDb, bookingDb
from Turf.serializers import Turf_Serializer, Booking_Serializer
from decimal import Decimal
from datetime import datetime



class TurfListCreateView(APIView):

    def get(self, request):
        qs = TurfDb.objects.all()
        serializer_instance = Turf_Serializer(qs, many=True)
        return Response(data=serializer_instance.data)
    
    def post(self, request):
        form_data = request.data
        serializer_instance = Turf_Serializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data,status=status.HTTP_201_CREATED)
        else:
            return Response(
                data=serializer_instance.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class TurfDetailsView(APIView):

    def get(self, request, id):
        try:
            qs = TurfDb.objects.get(id=id)
            serializer_instance = Turf_Serializer(qs)
            return Response(data=serializer_instance.data)
        except TurfDb.DoesNotExist:
            return Response(
                {"message": "Turf not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        try:
            qs = TurfDb.objects.get(id=id)
            serializer_instance = Turf_Serializer(qs, data=request.data)
            if serializer_instance.is_valid():
                serializer_instance.save()

                return Response(data=serializer_instance.data)

            else:
                return Response(data=serializer_instance.errors,status=status.HTTP_400_BAD_REQUEST)

        except TurfDb.DoesNotExist:

            return Response(
                {"message": "Turf not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, id):

        try:
            qs = TurfDb.objects.get(id=id)
            qs.delete()
            return Response(
                {"message": "Turf deleted successfully"}
            )
        except TurfDb.DoesNotExist:
            return Response(
                {"message": "Turf not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class BookingListCreateView(APIView):

    def get(self, request):
        qs = bookingDb.objects.all()
        serializer_instance = Booking_Serializer(qs, many=True)
        return Response(data=serializer_instance.data)
    def post(self, request):
        form_data = request.data
        serializer_instance = Booking_Serializer(data=form_data)
        if serializer_instance.is_valid():
            turf = serializer_instance.validated_data.get("turf")
            booking_date = serializer_instance.validated_data.get("booking_date")
            start_time = serializer_instance.validated_data.get("start_time")
            end_time = serializer_instance.validated_data.get("end_time")

            if start_time >= end_time:
                return Response(
                    {"message": "End time must be after start time"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not turf.is_available:
                return Response(
                    {"message": "Turf is not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            existing_booking = bookingDb.objects.filter(
                turf=turf,
                booking_date=booking_date,
                status="confirmed",
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if existing_booking:
                return Response(
                    {"message": "Turf is already booked for this time"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            start = datetime.combine(booking_date, start_time)
            end = datetime.combine(booking_date, end_time)
            total_hours = Decimal(
                str((end - start).total_seconds() / 3600)
            )
            total_price = (
                turf.price_per_hour * total_hours
            ).quantize(Decimal("0.01"))
            serializer_instance.save(total_price=total_price)
            return Response(
                {
                    "message": "Booking created successfully",
                    "booking": serializer_instance.data,
                    "total_price": total_price
                },
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                data=serializer_instance.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class BookingDetailsView(APIView):
    def get(self, request, id):
        try:
            qs = bookingDb.objects.get(id=id)
            serializer_instance = Booking_Serializer(qs)
            return Response(data=serializer_instance.data)
        except bookingDb.DoesNotExist:
            return Response(
                {"message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    def put(self, request, id):
        try:
            qs = bookingDb.objects.get(id=id)
            serializer_instance = Booking_Serializer(
                qs,
                data=request.data
            )
            if serializer_instance.is_valid():
                turf = serializer_instance.validated_data.get("turf", qs.turf )
                booking_date = serializer_instance.validated_data.get("booking_date", qs.booking_date)
                start_time = serializer_instance.validated_data.get( "start_time", qs.start_time)
                end_time = serializer_instance.validated_data.get("end_time", qs.end_time)
                if start_time >= end_time:
                    return Response(
                        {"message": "End time must be after start time"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                existing_booking = bookingDb.objects.filter(
                    turf=turf,
                    booking_date=booking_date,
                    status="confirmed",
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ).exclude(id=id).exists()

                if existing_booking:
                    return Response(
                        {"message": "Turf is already booked for this time"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                start = datetime.combine(booking_date, start_time)
                end = datetime.combine(booking_date, end_time)

                total_hours = Decimal(
                    str((end - start).total_seconds() / 3600)
                )

                total_price = (
                    turf.price_per_hour * total_hours
                ).quantize(Decimal("0.01"))

                serializer_instance.save(total_price=total_price)

                return Response(
                    {
                        "message": "Booking updated successfully",
                        "booking": serializer_instance.data
                    }
                )

            else:
                return Response(
                    data=serializer_instance.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except bookingDb.DoesNotExist:

            return Response(
                {"message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, id):
        try:
            qs = bookingDb.objects.get(id=id)
            qs.delete()
            return Response(
                {"message": "Booking deleted successfully"}
            )
        except bookingDb.DoesNotExist:
            return Response(
                {"message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )