set -x
adb uninstall 'com.estrongs.android.pop'
adb install 'apks/ES File Explorer File Manager_4.1.9.7.4_Apkpure.apk'
#adb install 'apks/com.stealthcopter.portdroid_0.6.22-78_minAPI21(arm64-v8a,armeabi-v7a,x86,x86_64)(nodpi)_apkmirror.com.apk'
adb install apks/com.stealthcopter.portdroid.apk
#adb install apks/QGroundControl64-20230428-daily.apk
adb install org.mavlink.qgrouncontrolbeta.apk
adb install apks/3DR Solo_2.4.0_APKPure.apk
adb install apks/Specta-v8.0.0-240924-542-57452-americaOfficial-sec.apk
adb install-multiple $(ls apks/MissionPlanner_98325_APKPure/*apk)
adb install apks/com-fognl-solex-163.apk

adb push ../frida/frida
# copy 3DR firmware files to phone
#adb shell rm /sdcard/Download/3dr*
adb push ../opensolo/3dr-controller.tar.gz /sdcard/Download
adb push ../opensolo/3dr-controller.tar.gz.md5 /sdcard/Download
adb push ../opensolo/3dr-solo.tar.gz /sdcard/Download
adb push ../opensolo/3dr-solo.tar.gz.md5 /sdcard/Download

# frida (nexus 6p are arm64)
# frida-tools 13.7.1
adb push frida/frida-server-16.7.19-android-arm64  /sdcard/Download
adb shell "cp /sdcard/Download/frida-server-16.7.19-android-arm64 /data/local/tmp"
adb shell "chmod +x /data/local/tmp/frida-server-16.7.19-android-arm64"

# autorun to start ES FileExplorer at boot
#adb install SevnAutorun.apk
#adb push SevnAutorun.db /sdcard/Download/SevnAutorun.db
#sleep 2
#adb shell run-as ru.org.sevn.autorun mkdir /data/data/ru.org.sevn.autorun/databases
#adb shell run-as ru.org.sevn.autorun cp /sdcard/Download/SevnAutorun.db /data/data/ru.org.sevn.autorun/databases/SevnAutorun.db
#adb shell run-as ru.org.sevn.autorun rm /sdcard/Download/SevnAutorun.db 
