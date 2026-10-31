/**
 * Barber SaaS - كود ربط صفحة الهبوط بـ Google Sheets
 * 
 * -------------------------------------------------------------
 * 📌 خطوات التثبيت في دقيقتين فقط:
 * 1. افتح صفحة إكسل جديدة في جوجل من الرابط: https://sheets.new
 * 2. من القائمة العلوية اضغط على: ملحقات (Extensions) -> Apps Script
 * 3. احذف أي كود موجود هناك، والصق هذا الكود كاملاً
 * 4. اضغط على زر "نشر" (Deploy) الأزرق في أعلى اليسار -> "نشر جديد" (New deployment)
 * 5. اضغط على الترس ⚙️ بجانب "Select type" واختر: تطبيق ويب (Web app)
 *    - الوصف: Barber SaaS Leads
 *    - تنفيذ باسم: حسابي (Me)
 *    - من يمكنه الوصول (Who has access): الجميع (Anyone)  ⚠️ خطوة أساسية!
 * 6. اضغط "نشر" (Deploy) ثم امنح الصلاحيات المطلوبة (Authorize access)
 * 7. انسخ "عنوان URL لتطبيق الويب" (Web App URL) الناتج، وأعطني إياه لنربطه لك فوراً!
 * -------------------------------------------------------------
 */

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // إنشاء ترويسة الجدول وتنسيقها تلقائياً إذا كان الملف فارغاً
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "المعرف #",
        "نوع التفاعل",
        "رقم الجوال",
        "تاريخ ووقت التسجيل",
        "نوع الجهاز",
        "معلومات المتصفح"
      ]);
      
      var headerRange = sheet.getRange(1, 1, 1, 6);
      headerRange.setFontWeight("bold");
      headerRange.setBackground("#0f766e");
      headerRange.setFontColor("#ffffff");
      headerRange.setHorizontalAlignment("center");
      sheet.setFrozenRows(1);
    }
    
    var id = sheet.getLastRow();
    var choice = data.choice === "interested" ? "مهتم ✓" : "غير مهتم ✕";
    
    // وضع فاصلة علوية قبل الرقم لكي يحافظ إكسل على الصفر الأولي (05xxxxxxxx)
    var phone = data.phone ? "'" + data.phone : "—";
    
    // التوقيت بتوقيت مكة المكرمة / السعودية
    var timestamp = Utilities.formatDate(new Date(), "Asia/Riyadh", "yyyy-MM-dd HH:mm:ss");
    var userAgent = data.user_agent || "";
    var device = parseDevice(userAgent);
    
    sheet.appendRow([id, choice, phone, timestamp, device, userAgent]);
    
    // تلوين الصف حسب الاهتمام
    var lastRow = sheet.getLastRow();
    if (data.choice === "interested") {
      sheet.getRange(lastRow, 2).setBackground("#dcfce7").setFontColor("#15803d").setFontWeight("bold");
      sheet.getRange(lastRow, 3).setFontWeight("bold").setHorizontalAlignment("center");
    } else {
      sheet.getRange(lastRow, 2).setBackground("#f1f5f9").setFontColor("#64748b");
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "success", "id": id }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "error", "message": err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function parseDevice(ua) {
  if (!ua) return "غير معروف";
  if (ua.indexOf("iPhone") > -1) return "📱 iPhone";
  if (ua.indexOf("Android") > -1) return "📱 Android";
  if (ua.indexOf("iPad") > -1) return "📱 iPad";
  if (ua.indexOf("Windows") > -1) return "💻 Windows PC";
  if (ua.indexOf("Macintosh") > -1) return "💻 Mac Desktop";
  return "💻 متصفح ويب";
}

