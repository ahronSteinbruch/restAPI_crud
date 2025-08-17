### **קובץ הדרכה: `docs/05_mongodb_openshift_deployment.md`**

#### **1. מטרת השלב**

מטרת שלב זה היא להגדיר את כל תשתית מסד הנתונים של MongoDB ב-OpenShift. אנו עושים זאת באמצעות קבצי YAML דקלרטיביים, המהווים "תשתית כקוד" (Infrastructure as Code). אנו יוצרים ארבעה אובייקטים חיוניים: `Secret` לניהול מאובטח של סיסמאות, `PersistentVolumeClaim` (PVC) להבטחת שמירת נתונים קבועה, `Deployment` להרצת קונטיינר ה-MongoDB, ו-`Service` לחשיפת מסד הנתונים לרשת הפנימית של הקלאסטר.

---

#### **2. הסבר מעמיק על האובייקטים שנוצרו (גישת ה-YAML)**

1.  **Secret (סוד):**
    *   **תפקיד:** אובייקט זה נועד לאחסן מידע רגיש, כמו סיסמאות, מפתחות API, או טוקנים. הנתונים ב-Secret נשמרים בצורה מוצפנת (או לפחות מקודדת) בתוך בסיס הנתונים הפנימי של OpenShift (etcd).
    *   **ההיגיון:** הפרדת סודות מהקוד ומתצורת ה-Deployment היא פרקטיקת אבטחה בסיסית. זה מונע חשיפת סיסמאות במאגרי Git ומאפשר לצוותי תפעול לנהל סיסמאות בנפרד מצוותי הפיתוח. במקרה שלנו, אנו שומרים בו את פרטי הגישה למשתמש הראשי של MongoDB.

2.  **PersistentVolumeClaim (PVC - תביעת אחסון קבועה):**
    *   **תפקיד:** Pods ב-OpenShift הם "בני חלוף"; אם הם נמחקים או קורסים, כל המידע על מערכת הקבצים שלהם נעלם. אפליקציות הדורשות שמירת מצב (stateful applications), כמו מסדי נתונים, חייבות לאחסן את המידע שלהן במיקום חיצוני וקבוע. ה-PVC הוא "בקשה" מהאפליקציה לתשתית OpenShift להקצות לה "דיסק" קבוע מהאחסון הזמין בקלאסטר.
    *   **ההיגיון:** על ידי חיבור ה-PVC לנתיב הנתונים של MongoDB (`/data/db`), אנו מבטיחים שגם אם ה-Pod של MongoDB יופעל מחדש, הוא יתחבר מחדש לאותו נפח אחסון והנתונים שלו יישמרו.

3.  **Deployment (פריסה):**
    *   **תפקיד:** זהו האובייקט המרכזי שמנהל את הרצת האפליקציה. הוא מגדיר איזה אימג' להריץ, כמה עותקים (replicas) שלו להריץ, ואיך להגדיר כל עותק.
    *   **ההיגיון:** ה-Deployment אחראי על שמירת "המצב הרצוי". אם Pod קורס, ה-Controller של ה-Deployment יזהה זאת וייצור Pod חדש במקומו באופן אוטומטי, ובכך יבטיח שהשירות תמיד זמין. הוא גם מחבר יחד את הקונטיינר עם התלות החיצונית שלו, כמו ה-Secret (כמשתני סביבה) וה-PVC (כ-volume).

4.  **Service (שירות):**
    *   **תפקיד:** ה-Service פותר את בעיית הרישות הפנימית בקלאסטר. לכל Pod יש כתובת IP פנימית, אך היא משתנה בכל פעם שה-Pod מופעל מחדש.
    *   **ההיגיון:** ה-Service יוצר נקודת גישה **קבועה** ויציבה עם שם DNS פנימי (למשל, `mongo-service`). הוא עוקב אחרי ה-Pods הבריאים שתואמים לתווית שהוגדרה לו, ומנתב את התעבורה אליהם. כך, שירותים אחרים (כמו ה-FastAPI שלנו) יכולים לתקשר עם מסד הנתונים באמצעות שם קבוע ופשוט, מבלי צורך לדעת את ה-IP המשתנה של ה-Pod עצמו.

---

#### **3. חלופות ושיקולים**

*   **חלופה מרכזית: הקמת התשתית באמצעות פקודות `oc` (גישה אימפרטיבית)**

    במקום לכתוב ולהפעיל קבצי YAML, ניתן להשיג תוצאה דומה באמצעות סדרה של פקודות `oc` ישירות. גישה זו מהירה לבדיקות אך פחות מומלצת לסביבות ייצור.

    **שלב א': יצירת ה-Secret באמצעות פקודה:**
    הפקודה `oc create secret generic` מאפשרת ליצור Secret ישירות משורת הפקודה.
    ```bash
    oc create secret generic mongo-credentials \
      --from-literal=MONGO_INITDB_ROOT_USERNAME='mongoadmin' \
      --from-literal=MONGO_INITDB_ROOT_PASSWORD='very_strong_password' \
      --from-literal=MONGO_DB_NAME='mydatabase'
    ```
    *   **הסבר:** אנו יוצרים Secret מסוג `generic` בשם `mongo-credentials`. הדגל `--from-literal` מאפשר להגדיר כל זוג מפתח-ערך בנפרד.

    **שלב ב': יצירת ה-PVC (מומלץ עדיין להשתמש ב-YAML קצר):**
    יצירת PVC באמצעות פקודה ישירה היא מסורבלת. הדרך היעילה ביותר היא להשתמש בקובץ YAML קצר גם בגישה זו.
    ```bash
    # שמור את הטקסט הבא בקובץ זמני, למשל 'pvc.yaml', והרץ 'oc apply -f pvc.yaml'
    # apiVersion: v1
    # kind: PersistentVolumeClaim
    # metadata:
    #   name: mongo-pvc
    # spec:
    #   accessModes:
    #     - ReadWriteOnce
    #   resources:
    #     requests:
    #       storage: 2Gi
    ```

    **שלב ג': יצירת ה-Deployment וה-Service באמצעות `oc new-app`:**
    פקודה זו יוצרת באופן אוטומטי גם `Deployment` וגם `Service`.
    ```bash
    oc new-app mongo:6.0 --name=mongo-app
    ```

    **שלב ד': חיבור ה-Secret וה-PVC ל-Deployment שנוצר:**
    לאחר שה-Deployment נוצר, אנו משתמשים בפקודות `oc set` כדי לשנות אותו ולהוסיף לו את התלות.
    ```bash
    # חבר את ה-Secret כמשתני סביבה
    oc set env deployment/mongo-app --from=secret/mongo-credentials

    # חבר את ה-PVC כ-Volume
    oc set volume deployment/mongo-app --add \
      --name=mongo-persistent-storage \
      --type=persistentVolumeClaim \
      --claim-name=mongo-pvc \
      --mount-path=/data/db
    ```
    *   **הסבר:**
        *   `oc set env`: מעדכן את משתני הסביבה של Deployment קיים.
        *   `oc set volume`: מוסיף `Volume` ו-`VolumeMount` ל-Deployment קיים, ומחבר את ה-PVC שלנו לנתיב הנכון בקונטיינר.

*   **StatefulSet במקום Deployment:**
    *   **הסבר:** `StatefulSet` הוא אובייקט Kubernetes המיועד לאפליקציות הדורשות "מצב" יציב, כמו מסדי נתונים. הוא מספק זהות רשת יציבה וקבועה לכל Pod, מה שחיוני להקמת קלאסטר של מסדי נתונים עם מספר עותקים. עבור מופע בודד של MongoDB, `Deployment` הוא פתרון פשוט ומספק, אך חשוב להכיר את `StatefulSet` כחלופה הנכונה לתרחישים מורכבים יותר.

