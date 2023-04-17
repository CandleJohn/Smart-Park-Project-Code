const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();

const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'smartparkdb',
    port: '3307',
});

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({extended:true}));

app.listen(5002, () => {
    console.log("running on port 5002");
})

app.get('/', (req, res) => {
    res.send('Hello');
})

// Login driver 
app.get("/LoginDriver", (req, res) => {
    const sqlLogin = "SELECT * FROM drivers WHERE email=? and password=?";
    const email = req.query.loginEmail;
    const password = req.query.loginPassword;

    db.query(sqlLogin, [email,password], (err, result) => {
        console.log(err);
        res.send(result[0]);
    })
})

// get all bookings made by logged in driver
app.post("/driverBookings", (req, res) => {
    const sqlBookings = "SELECT booking_id, booking_date, booking_cost, registration FROM bookings b JOIN vehicles v ON b.vehicle_id = v.vehicle_id WHERE v.driver_id=?";
    const driverId = req.query.driver_id;
    console.log(req.query.driver_id);

    db.query(sqlBookings, driverId, (err, result) => {
        console.log(err);
        console.log(result);
        res.send(result);
    })
})

// get all vehicle associated with logged in driver
app.post("/userVehicles", (req,res)=>{
    const sqlVehicles = "SELECT * FROM vehicles WHERE driver_id=?";
    const driverId = req.query.driverId;

    db.query(sqlVehicles, driverId, (err, result) => {
        console.log(err);
        console.log(result);
        res.send(result);
    })
})

//get a vehicle by vehicle id
app.post("/getVehicle", (req, res) => {
    const sqlGetVehicle = "SELECT * FROM vehicles WHERE vehicle_id=?";
    const vehicle_id = req.query.vehicle_id;

    db.query(sqlGetVehicle, vehicle_id, (err, result) => {
        console.log(err);
        console.log(result);
        res.send(result[0]);
    })
}
)

// add a vehicle
app.post("/addVehicle", (req, res) => {
    const sqlAddVehicle = "INSERT INTO vehicles (registration, colour, model, brand, driver_id) VALUES (?,?,?,?,?)";
    const registration = req.query.registration;
    const colour = req.query.colour;
    const model = req.query.model;
    const brand = req.query.brand;
    const driverId = req.query.driverId;

    db.query(sqlAddVehicle, [registration, colour, model, brand, driverId], (err, result) => {
        console.log(err);
        res.send(result);
    })
})

// update a vehicle
app.put("/updateVehicle", (req, res) => {
    const sqlUpdateVehicle = "UPDATE vehicles SET registration=?, colour=?, model=?, brand=? WHERE vehicle_id=?";
    const vehicleId = req.query.vehicle_id;
    const registration = req.query.registration;
    const colour = req.query.colour;
    const brand = req.query.brand;
    const model = req.query.model;

    db.query(sqlUpdateVehicle, [registration, colour, model, brand, vehicleId], (err, result) => {
        console.log(err);
        res.send(result);
    })
})

// delete a vehicle
app.delete("/deleteVehicle", (req, res) => {
    const sqlDeleteVehicle = "DELETE FROM vehicles WHERE vehicle_id=?";
    const vehicleId = req.query.vehicle_id;

    db.query(sqlDeleteVehicle, vehicleId, (err, result) => {
        console.log(err);
        res.send(result);
    })
})

// register new user
app.post("/registerUser", (req,res) => {
    const sqlRegisterUser = "INSERT INTO drivers (first_name, last_name, email, phone, password) VALUES (?,?,?,?,?)";
    const firstName = req.query.firstName;
    const lastName = req.query.lastName;
    const email = req.query.email;
    const phone = req.query.phone;
    const password = req.query.password;

    db.query(sqlRegisterUser, [firstName,lastName,email, phone, password], (err, result) => {
        // console.log(err);
        console.log("Inserted: "+ result.insertId);
        driverId = result.insertId;
        res.send(driverId.toString())
    })
})

// update driver
app.post("/updateUser", (req,res) => {
    const sqlUpdateDriver = "UPDATE drivers SET first_name=?, last_name=?, email=?, phone=? WHERE driver_id=?"
    const driver_id = req.query.driver_id;
    const fName = req.query.firstName;
    const lName = req.query.lastName;
    const email = req.query.email;
    const phone = req.query.phone;
    db.query(sqlUpdateDriver, [fName, lName, email, phone, driver_id], (err, result) => {
        console.log("Updated: " + driver_id)
        console.log(err);
        res.send(result);
    })
})

// check registraion
app.post("/checkRegistration", (req, res) => {
    const sqlCheckReg = "SELECT driver_id, vehicle_id FROM vehicles WHERE registration=?"
    const registration = req.body.registration;
    db.query(sqlCheckReg, registration, (err, result) => {
        console.log(err);
        res.send(result);
    })
})

// add booking
app.post("/addBooking", (req,res) => {
    const sqlAddBooking = "INSERT INTO bookings (booking_date, booking_cost, booking_duration, vehicle_id) VALUES (?,?,?,?)";
    const date = req.body.bookingDate
    const cost = req.body.bookingCost
    const duration = req.body.bookingDuration
    const vehicleId = req.body.vehicleId
    db.query(sqlAddBooking, [date, cost, duration, vehicleId], (err, result) => {
        console.log(err)
        res.send(result)
    })
})
