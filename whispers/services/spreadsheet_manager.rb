require 'google/apis/sheets_v4'
require 'googleauth'

class SpreadsheetManager
  SPREADSHEET_ID = '1Yx0n4ixRIX9d-qMl6BGsW2oYErC6BUH4ILtVT0fQkxk'  # 실제 스프레드시트 ID로 교체
  RANGE = 'Rumors!A:E'  # 데이터를 저장할 시트와 범위

  def initialize
    @service = Google::Apis::SheetsV4::SheetsService.new
    @service.authorization = Google::Auth::ServiceAccountCredentials.from_env(
      "GOOGLE_CREDENTIALS"
    )
  end

  def save_rumor(rumor)
    values = [
      [
        rumor.id,
        rumor.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        rumor.character_name,
        rumor.content,
        rumor.influence_level
      ]
    ]

    request_body = Google::Apis::SheetsV4::ValueRange.new(values: values)
    @service.append_spreadsheet_value(
      SPREADSHEET_ID,
      RANGE,
      request_body,
      value_input_option: 'RAW'
    )
  end

  def get_recent_rumors(limit = 10)
    response = @service.get_spreadsheet_values(SPREADSHEET_ID, RANGE)
    return [] unless response.values

    response.values.last(limit).map do |row|
      Rumor.new(
        id: row[0],
        timestamp: Time.parse(row[1]),
        character_name: row[2],
        content: row[3],
        influence_level: row[4].to_i
      )
    end
  end
end
