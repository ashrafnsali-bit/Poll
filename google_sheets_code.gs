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

    // التأكد من وجود وتنسيق بطاقة النسبة المئوية والإحصائيات التفاعلية
    ensureSummaryCard(sheet);
    
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

// دالة بناء وتحديث بطاقة النسبة المئوية الذكية في الأعمدة H و I
function ensureSummaryCard(sheet) {
  var titleCell = sheet.getRange("H1").getValue();
  if (titleCell !== "📊 ملخص ونتائج الاستفتاء") {
    // 1. عنوان البطاقة
    sheet.getRange("H1:I1").merge()
      .setValue("📊 ملخص ونتائج الاستفتاء")
      .setFontWeight("bold")
      .setFontSize(11)
      .setBackground("#0f766e")
      .setFontColor("#ffffff")
      .setHorizontalAlignment("center");

    // 2. إجمالي التفاعلات
    sheet.getRange("H2").setValue("إجمالي التفاعلات").setFontWeight("bold").setBackground("#f8fafc");
    sheet.getRange("I2").setFormula('=COUNTA(B2:B)').setFontWeight("bold").setHorizontalAlignment("center");

    // 3. عدد المهتمين
    sheet.getRange("H3").setValue("عدد المهتمين ✓").setFontWeight("bold").setBackground("#f0fdf4").setFontColor("#15803d");
    sheet.getRange("I3").setFormula('=COUNTIF(B2:B, "*مهتم*")').setFontWeight("bold").setHorizontalAlignment("center").setFontColor("#15803d");

    // 4. عدد غير المهتمين
    sheet.getRange("H4").setValue("عدد غير المهتمين ✕").setFontWeight("bold").setBackground("#f8fafc").setFontColor("#64748b");
    sheet.getRange("I4").setFormula('=COUNTIF(B2:B, "*غير مهتم*")').setFontWeight("bold").setHorizontalAlignment("center").setFontColor("#64748b");

    // 5. نسبة الاهتمام المئوية الرئيسية
    sheet.getRange("H5").setValue("🔥 نسبة الاهتمام").setFontWeight("bold").setFontSize(11).setBackground("#15803d").setFontColor("#ffffff");
    sheet.getRange("I5").setFormula('=IF(COUNTA(B2:B)>0, COUNTIF(B2:B, "*مهتم*")/COUNTA(B2:B), 0)')
      .setNumberFormat("0.0%")
      .setFontWeight("bold")
      .setFontSize(13)
      .setBackground("#dcfce7")
      .setFontColor("#15803d")
      .setHorizontalAlignment("center");

    // 6. نسبة غير المهتمين
    sheet.getRange("H6").setValue("نسبة غير المهتمين").setFontWeight("bold").setBackground("#f1f5f9").setFontColor("#64748b");
    sheet.getRange("I6").setFormula('=IF(COUNTA(B2:B)>0, COUNTIF(B2:B, "*غير مهتم*")/COUNTA(B2:B), 0)')
      .setNumberFormat("0.0%")
      .setFontWeight("bold")
      .setBackground("#f8fafc")
      .setFontColor("#64748b")
      .setHorizontalAlignment("center");

    // تنسيق الحدود والفواصل
    sheet.getRange("H1:I6").setBorder(true, true, true, true, true, true, "#cbd5e1", SpreadsheetApp.BorderStyle.SOLID);
    
    // ضبط أحجام الأعمدة تلقائياً
    sheet.setColumnWidth(7, 30);  // عمود فاصل فارغ G
    sheet.setColumnWidth(8, 160); // العمود H للتسميات
    sheet.setColumnWidth(9, 130); // العمود I للقيم والنسب
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

