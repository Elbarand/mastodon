# app/controllers/registrations_controller.rb
class RegistrationsController < Devise::RegistrationsController
  def create
    invite_code = InviteCode.find_by(code: params[:invite_code])

    unless invite_code && !invite_code.used?
      flash[:alert] = '유효하지 않은 초대 코드입니다.'
      redirect_to new_user_registration_path and return
    end

    super do |resource|
      if resource.persisted?
        invite_code.update(used: true, user: resource)
      end
    end
  end
end