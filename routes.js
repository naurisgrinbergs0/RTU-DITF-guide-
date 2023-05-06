const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();

// returns all the existing cabinets
router.get('/api/getcabinets', (req, res) => {
    // open database
    const db = new sqlite3.Database('./path_finder/database/project_map.sqlite');

    // get cabinets from the database
    db.all(`SELECT * FROM cabinets_array`, [], (err, rows) => {
        if (err) {
            console.error(err.message);
        } else {
            const data = {cabinets: []};
            rows.forEach(row => {
                data.cabinets.push({
                    id: row.id,
                    cabinet: row.cabinet_nr,
                    floor: row.floor
                })
            });
            
            // return cabinets as json array
            res.json(data);
        }
    });
});


// generates directions
router.get('/api/getdirections', (req, res) => {
    // call python script that generates directions
    const { spawn } = require('child_process');
    const pythonScript = './path_finder/main.py';

    // pass arguments to script
    const arguments = [
        req.query.cabinet_start, 
        req.query.cabinet_end,
        req.query.floor_start,
        req.query.floor_end,
        req.query.use_elevator,
        req.query.language,
    ];

    // spawn a child process and execute the Python script
    const pythonProcess = spawn('python', [pythonScript, ...arguments]);

    // listen for stdout data from the Python script
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python script stdout: ${data}`);
        res.json(data.toString());
    });

    // listen for stderr data from the Python script
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python script stderr: ${data}`);
    });

    // listen for the Python script to exit
    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
    });

});


module.exports = router;
