# frozen_string_literal: true

class AddAccountsToListService < BaseService
  def call(user, list, account_ids)
    raise ActiveRecord::RecordNotFound unless list.account_id == user.account_id

    accounts = Account.where(id: account_ids)

    ListAccount.transaction do
      accounts.each do |account|
        ListAccount.find_or_create_by!(list: list, account: account)
      end
    end
  end
end