describe("search dataset by spatial bounding boxes and boundaries", ()=>{
    //TODO: add a dataset that has these values
    beforeEach(()=>{
        cy.visit("/dataset/")
    })
    it("applies spatial search via arbitrary bounding box",()=>{
        cy.get(".leaflet-draw-draw-rectangle")
        .click()
        cy.get("#dataset-map-container")
        .trigger('mousedown',  350, 110, {which:1})
        //.trigger('mousedown')
        .trigger('mousemove', { clientX: 600, clientY: 236 })
        .trigger('mouseup', {force:true})
        .get(".apply").click()
    })

    it("applies spatial search via proximity cricle", ()=>{
        cy.get(".leaflet-draw-draw-circle")
        .click()
        cy.get("#dataset-map-container")
        .trigger('mousedown',   100, 110, {which:1})
        //.trigger('mousedown')
        .trigger('mousemove', 200, 50)
        .trigger('mouseup', {force:true})
        .get(".apply").click()
    })

    it("applies spatial search via spatial layer", ()=>{
        cy.get(".leaflet-control-layers-toggle")
        .click()
        cy.get("#dataset-map-container")
        .trigger('mousedown',   200, 50, {which:1})
        .get(".apply").click()
    })

})
