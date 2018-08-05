Some notes for my Sonoff setup:
- I've set up time and timezones so that I can run time-based automations directly on the devices.
  - TimeSTD 0,1,11,1,2,-480 Sets standard time
  - TimeDST 0,2,3,1,2,-420 Sets DST
  - Timezone 99 Enables using DST settings
  - NtpServer1 192.168.1.1 Use my local NTP server
- Automatic restart: rule1 on Time#Minute=120 do Restart 1
  - Currently only set on bike room lamp
- Disable Serial output once tested and working
  - seriallog 0
