from pyteal import *

def song_registry_contract():
    # Global state keys
    song_count_key = Bytes("song_count")
    
    # Helper functions
    def get_song_key(song_id):
        return Concat(Bytes("song_"), Itob(song_id))
    
    # Register a new song
    register_song = Seq([
        App.globalPut(song_count_key, 
            If(App.globalGet(song_count_key) == Int(0))
            .Then(Int(1))
            .Else(App.globalGet(song_count_key) + Int(1))
        ),
        
        App.globalPut(
            get_song_key(App.globalGet(song_count_key) - Int(1)),
            Concat(
                Txn.application_args[1], Bytes("|"),  # title
                Txn.application_args[2], Bytes("|"),  # url  
                Txn.sender()                          # owner
            )
        ),
        App.globalPut(
            get_song_key(App.globalGet(song_count_key) - Int(1), "price"),
            Btoi(Txn.application_args[3])
        ),
        
        Approve()
    ])
    
    # Main contract logic
    program = Cond(
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.NoOp, 
         Cond(
             [Txn.application_args[0] == Bytes("register_song"), register_song],
             [Txn.application_args[0] == Bytes("get_song_count"), 
              Return(App.globalGet(song_count_key))]
         )],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Txn.sender() == Global.creator_address())],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Txn.sender() == Global.creator_address())]
    )
    
    return program

if __name__ == "__main__":
    # Compile the contract
    approval_program = compileTeal(song_registry_contract(), Mode.Application, version=6)
    
    # Clear state program (simple approval)
    clear_program = compileTeal(Approve(), Mode.Application, version=6)
    
    # Save compiled programs
    with open("song_registry_approval.teal", "w") as f:
        f.write(approval_program)
    
    with open("song_registry_clear.teal", "w") as f:
        f.write(clear_program)
    
    print("Smart contract compiled!")
    print("Files created: song_registry_approval.teal, song_registry_clear.teal")


