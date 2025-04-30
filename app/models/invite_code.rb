# app/models/invite_code.rb
class InviteCode < ApplicationRecord
  belongs_to :user, optional: true
  before_create :generate_code

  validates :code, uniqueness: true

  def self.valid_code?(code)
    exists?(code: code, used: false)
  end

  private

  def generate_code
    self.code = SecureRandom.hex(10)
  end
end