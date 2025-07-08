import apluggy as pluggy
from lyikpluginmanager import getProjectName, VerifyHandlerSpec, VerifyHandlerResponseModel, VERIFY_RESPONSE_STATUS, ContextModel
from lyikpluginmanager.annotation import RequiredEnv
import logging
from ..model.irctcbookingform import RootPassengerInfo,RootJourneyInfo,RootTrainTicketInfo,RootPlatformTicketInfo,RootPaymentDetailsInfo,RootTrackingInfo,RootCancelBookingInfo
import re

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

def is_valid_email(email:str)-> bool:
    if not email:
        return False
    return bool(re.fullmatch("[^@\s]+@[^@\s]+\.[^@\s]+",email))

def is_valid_phone(phone:str)-> bool:
    if not phone:
        return False
    return bool(re.fullmatch(r"^[6-9]\d{9}$",phone))

class passengerVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(self,context:ContextModel,payload:RootPassengerInfo)->VerifyHandlerResponseModel:
        passenger = payload.Passenger_card
        if not passenger:
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Passenger details are missing."
                    )

        if not passenger.name or not passenger.age or not passenger.mobile or not passenger.email:
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Name, age, mobile number, and email are required."
                    )

        if not (1 <= len(passenger.name) <= 30):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Name must be between 1 and 30 characters."
                    )

        if not (20 <= passenger.age <= 60):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Age must be between 20 and 60."
                    )

        if not is_valid_phone(passenger.mobile):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Invalid mobile number. It should be 10 digits starting with 6, 7, 8, or 9."
                    )

        if not is_valid_email(passenger.email):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message="Invalid email format."
                    )

        return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.SUCCESS,
                    message="Passenger information verified successfully."
                )
    

# Journey Info Verification Handler
class JourneyVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(self, context: ContextModel, payload: RootJourneyInfo) -> VerifyHandlerResponseModel:
        journey = payload.jounery_card

        if not journey:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Journey details are missing."
            )

        if not journey.from_station or not journey.to_station or not journey.journey_date:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="From Station, To Station and Journey Date are required."
            )

        if not journey.train_number or not journey.train_name:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Train Number and Train Name are required."
            )

        if not journey.quota or journey.quota.upper() not in ["GENERAL", "TATKAL"]:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Quota must be 'General' or 'Tatkal'."
            )

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message="Journey details verified successfully."
        )
# Train Ticket Booking Verification Handler

class TrainTicketBookingVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(self, context: ContextModel, payload: RootTrainTicketInfo) -> VerifyHandlerResponseModel:
        booking = payload.booking_card

        if not booking:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Booking information is missing."
            )

        if not booking.jounery_reference_id:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Journey Reference ID is required."
            )

        if not booking.number_of_passengers or booking.number_of_passengers <= 0:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Number of passengers must be greater than 0."
            )

        if not booking.total_fare or booking.total_fare <= 0:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Total fare must be greater than 0."
            )

        if booking.booking_confirmed is None:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Booking confirmed status must be provided."
            )

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message="Train ticket booking verified successfully."
        )
    
class PlatformTicketVerfication(VerifyHandlerSpec):
      @impl

      async def verify_handler(self,context:ContextModel,payload:RootPlatformTicketInfo) -> VerifyHandlerResponseModel:
            PlatformTicket = payload.plantform_ticket_card

            if not PlatformTicket:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Missing platform ticket information."
                  )
            if not PlatformTicket.station_name or not PlatformTicket.number_of_ticket or not PlatformTicket.total_amount or not PlatformTicket.payment:
                  return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "All fields are required for platform ticket."
                  )
            if  PlatformTicket.number_of_ticket <= 0:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Number of tickets must be greater than zero."
                  )
            if PlatformTicket.total_amount <= 0:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Total amount must be positive."
                  ) 
            return VerifyHandlerResponseModel(
                  status = VERIFY_RESPONSE_STATUS.SUCCESS,
                  message = "Platform ticket verified."
            )

# Payment Verification Plugin
class PaymentVerification(VerifyHandlerSpec):
      async def verify_handler(self,context:ContextModel,payload:RootPaymentDetailsInfo)-> VerifyHandlerResponseModel:
            paymentCard = payload.payment_card

            if not paymentCard:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Payment details are missing"
                  )
            if not paymentCard.card_number or not len(str(paymentCard.card_number)) != 16:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Invalid card number. It must be 16 digits."
                  )
            if not paymentCard.card_holder or not (1<= len(str(paymentCard.card_holder)) <= 30):
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Card holder name must be 1 to 30 characters."
                  )
            if not paymentCard.expiry_date:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Expiry date is required."
                  )
            if not paymentCard.cvv :
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "CVV must be a 3-digit number."
                  )
            return VerifyHandlerResponseModel(
                  status =  VERIFY_RESPONSE_STATUS.SUCCESS,
                  message = "Payment information verified successfully."
            )

## Verification Plugin for Booking Tracking

class BookingTrackingVerification(VerifyHandlerSpec):
      async def verify_handler(self,context:ContextModel,payload:RootTrackingInfo) -> VerifyHandlerResponseModel:
            
            Tracking = payload.tracking_card

            if not Tracking:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Tracking card data is missing"
                  )
            if not Tracking.pnr_number or len(Tracking.pnr_number.strip()) <10:
                  return VerifyHandlerResponseModel(
                        status= VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Invalid PNR number. It should be at least 10 characters."
                  )
            if not Tracking.booking_status:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Booking status is required."
                  )
            if not Tracking.seat_number :
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Seat/Berth number is required."
                  )
            if not Tracking.coach_number:
                  return  VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Coach number is required."
                  )
            return VerifyHandlerResponseModel(
                  status = VERIFY_RESPONSE_STATUS.SUCCESS,
                  message = "Booking tracking details verified successfully."
            )
      
class CancelTicketVerification(VerifyHandlerSpec):
      async def verify_handler(self,context:ContextModel,payload:RootCancelBookingInfo) -> VerifyHandlerResponseModel:
            Cancel = payload.cancel_card

            if not Cancel:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Cancel card data is missing."
                  )
            if not Cancel.cancel_reason or len(Cancel.cancel_reason.strip()) < 5:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Reason for cancellation must be at least 5 characters."
                  )
            if not Cancel.refund_account or len(Cancel.refund_account) <5:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Refund account is required and must be valid."
                  )
            if not Cancel.confirm_cancel:
                  return VerifyHandlerResponseModel(
                        status = VERIFY_RESPONSE_STATUS.FAILURE,
                        message = "Cancellation must be confirmed."
                  )
            return VerifyHandlerResponseModel(
                  status = VERIFY_RESPONSE_STATUS.SUCCESS,
                  message = "Cancellation verified successfully."
            )